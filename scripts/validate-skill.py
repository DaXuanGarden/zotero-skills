#!/usr/bin/env python3
"""Statically validate the zotero-evidence-review skill markdown.

This script checks SKILL.md structure, required workflow text, templates,
and safety guards. It does not connect to Zotero or execute PubMed/external
search workflows.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - fallback for minimal environments
    yaml = None

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = REPO_ROOT / "zotero-evidence-review" / "SKILL.md"
LITERATURE_SEARCH_WRITER_PATH = REPO_ROOT / "scripts" / "write_literature_search_package.py"
LITERATURE_SEARCH_WRITER_FIXTURE_PATH = REPO_ROOT / "scripts" / "fixtures" / "literature_search_package_sample.json"
LITERATURE_SEARCH_WRITER_REQUIRED_TOP_LEVEL_KEYS = (
    "run",
    "topic_decomposition",
    "query_expansion",
    "criteria",
    "findings",
    "candidates",
    "reading_order",
    "reproducibility",
    "critical_warnings",
)
REQUIRED_TEMPLATES = (
    "REFS_BLOCK",
    "CLAIM_EVIDENCE_MATRIX",
    "WRITING_SUGGESTIONS_TABLE",
    "DIFF_REVISED_PARAGRAPH",
    "LITERATURE_SEARCH_REPORT",
    "EVIDENCE_REVIEW_REPORT",
    "MANUSCRIPT_STRATEGIC_REVIEW",
    "RIS_REFERENCE_FILE",
    "VERIFICATION_REPORT",
    "RECALL_AUDIT",
    "ZOTERO_IMPORT_HANDOFF",
    "ENDNOTE_IMPORT_HANDOFF",
    "ENDNOTE_COLLECTION_MANIFEST",
    "WRITING_OPTIONS_CARD",
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
    "## 1.8 Target Literature Search and Export",
    "## 1.9 Recall-first candidate retrieval",
    "## 2. Paragraph Evidence & Citation Analysis",
    "## 2.5 Evidence Package Export",
    "## 2.8 Manuscript-Level Thinking Checkpoint",
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
LITERATURE_SEARCH_REPORT_SECTIONS = [
    "## 1. 检索任务",
    "## 2. Topic Decomposition",
    "## 3. Query Expansion Plan",
    "## 4. 纳入与排除标准",
    "## 5. 结果分类标准",
    "## 6. 核心发现",
    "## 7. 检索结果总表",
    "## 8. 分类结果",
    "## 9. 噪音与排除原因",
    "## 10. 推荐阅读顺序",
    "## 11. Search Reproducibility",
    "## 12. Metadata QC",
    "## 13. Export Files",
]
TARGET_LITERATURE_SEARCH_REQUIREMENTS = [
    "target_literature_search",
    "Module 1.8: Target Literature Search and Export",
    "Target literature search separation",
    "Target search export request",
    "which papers use X",
    "search Zotero for X",
    "export a literature list/report/RIS",
    "Copy-ready Manuscript Text",
    "sentence-level citation placement",
    "paragraph diff",
    "Core output is a literature search report, not a paragraph evidence package",
    "Zotero readiness smoke test",
    "semantic search for broad recall",
    "keyword searches for precise concepts",
    "candidate pooling",
    "deduplicate by DOI / title / Zotero key",
    "classify candidates into Core / Strong Related / Method Background / Disease GWAS Only / Noise / Verify",
    "LITERATURE_SEARCH_REPORT",
    "Generated Literature Search Package:",
    "{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_literature_search.md",
    "Search Report + RIS",
    "Chat Search",
    "Search Report",
]
TARGET_LITERATURE_CLASSIFICATION_REQUIREMENTS = [
    "Core",
    "Strong Related",
    "Method Background",
    "Disease GWAS Only",
    "Noise",
    "Verify",
    "Literature Classification",
    "Default RIS action",
    "Category = Core",
]
SEARCH_RIS_REQUIREMENTS = [
    "Search RIS",
    "Citation RIS",
    "selected literature set",
    "not manuscript citation placement",
    "Do not require Copy-ready Manuscript Text or sentence-level citation recommendations before writing RIS",
    "Core included by default",
    "Strong Related",
    "Method Background",
    "Disease GWAS Only",
    "Noise",
    "Verify",
    "RIS action = Verify",
]
PHASE2_TARGET_SEARCH_REQUIREMENTS = [
    "Topic Decomposition Rules",
    "target object",
    "data/method/phenotype/cohort",
    "must-have concepts",
    "adjacent concepts",
    "exclusion concepts",
    "time/source constraints",
    "Query Expansion Matrix",
    "semantic query",
    "keyword query",
    "exact phrase query",
    "Negative / noise-control query",
    "Classification Decision Rubric",
    "Tie-breaker rules",
    "Noise / Exclusion Reasons",
    "wrong data layer",
    "disease-only GWAS",
    "method-only",
    "generic catalog",
    "metadata insufficient",
    "duplicate",
    "off-topic",
    "wrong population",
    "no inspected metadata",
]
PHASE3_LITERATURE_SEARCH_WRITER_REQUIREMENTS = [
    "scripts/write_literature_search_package.py",
    "--input candidates.json",
    "--output-root",
    "--slug",
    "--timestamp",
    "--include-optional",
    "--no-ris",
    "--dry-run",
    "--self-test",
    "JSON is required",
    "YAML is accepted only when PyYAML is already installed",
    "does not call Zotero or PubMed",
    "run",
    "topic_decomposition",
    "query_expansion",
    "criteria",
    "findings",
    "candidates",
    "reading_order",
    "reproducibility",
    "critical_warnings",
    "PubMed-only records require `pubmed_status = Completed` and `metadata_inspected = true`",
    "RIS default writes only `RIS action = Include`",
    "never writes `Exclude` or `Verify` records to Search RIS",
    "scripts/fixtures/literature_search_package_sample.json",
]
PHASE3_WRITER_SCRIPT_REQUIREMENTS = [
    "REQUIRED_TOP_LEVEL_KEYS",
    "ALLOWED_CATEGORIES",
    "ALLOWED_RIS_ACTIONS",
    "ALLOWED_EXCLUSION_CODES",
    "RIS_INCLUDE_CATEGORIES",
    "RIS_OPTIONAL_CATEGORIES",
    "write_literature_search_package.py",
    "--input",
    "--output-root",
    "--slug",
    "--timestamp",
    "--include-optional",
    "--no-ris",
    "--dry-run",
    "--self-test",
    "YAML input requires PyYAML",
    "does not search Zotero or PubMed",
    "metadata_inspected",
    "pubmed_status",
    "Completed",
    "ris_action",
    "Include",
    "Optional",
    "Exclude",
    "Verify",
    "generated RIS contains no records",
    "does not start with TY  -",
    "does not end with ER  -",
    "Self-test passed.",
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
    "WRITING_OPTIONS_CARD",
    "option_id",
    "rhetorical_angle",
    "selection_status: pending",
    "RIS action = Optional",
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
    "SENTENCE_CITATION_MATRIX",
    "CITATION_COVERAGE_SUMMARY",
    "sentence_id → claim_id → citation → RIS action",
    "citation_required",
    "citation_optional",
    "current_study",
    "common_knowledge",
    "interpretive_bridge",
    "RIS candidates without a sentence/claim mapping",
]

ROUTE_CONTRACT_REQUIREMENTS = [
    "## 0.1 Route contract: one request, one evidence owner",
    "zotero-literature-learning",
    "zotero-manuscript-thinking",
    "source_layer",
    "inspection_status",
    "stop_reason",
]

RECALL_FIRST_REQUIREMENTS = [
    "references/recall-first-retrieval.md",
    "high recall",
    "zotero_semantic",
    "zotero_structured",
    "pubmed_broad",
    "pubmed_design_or_method",
    "pubmed_related",
    "recall_status",
    "coverage_gaps",
    "two consecutive query rounds",
    "ZOTERO_IMPORT_HANDOFF",
    "zotero_import_status",
    "zotero_add_by_doi",
    "zotero_update_search_database",
    "never invent a Zotero item key",
    "ENDNOTE_IMPORT_HANDOFF",
    "format-references-endnote",
    "endnote-workflow",
    "bib-formatter",
    "direct library write: not supported",
]
ENDNOTE_COLLECTION_REQUIREMENTS = [
    "references/endnote-section-collections.md",
    "section-aware handoff",
    "Discussion/Discussion-01",
    "Methods/Methods-02",
    "write_endnote_collection_package.py",
    "one deduplicated master RIS",
    "selective per-group RIS files",
    "Manuscript section",
    "Manuscript paragraph",
    "Manuscript group",
    "Evidence role",
    "Unassigned/Unassigned",
    "import master RIS once",
    "direct_library_write: not supported",
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
DUAL_MCP_AUTO_EXPORT_REQUIREMENTS = [
    "Dual-MCP Auto Search and Export Defaults",
    "Dual-MCP auto search",
    "Automatic export by default",
    "ordinary `search`, `target_literature_search`, paragraph citation matching, paragraph polishing",
    "Module 1 ordinary Zotero search default output is **Search Report + RIS**",
    "Ordinary search auto-exports Search Report + RIS",
    "automatic PubMed expansion for biomedical topics when visible",
    "PubMed truth boundary",
    "never create PubMed-only RIS records from planned, failed, or uninspected PubMed results",
    "Search mode | target_literature_search / search",
    "Use `LITERATURE_SEARCH_REPORT` for target_literature_search and ordinary Module 1 search exports",
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
ZOTERO_SEQUENTIAL_GUARDRAIL_REQUIREMENTS = [
    "Zotero Sequential Execution Guardrail",
    "Zotero discovery and Zotero item inspection as a dependency chain, not a batch job",
    "Do not schedule `zotero_search_items`, `zotero_semantic_search`, or `zotero_advanced_search` in the same tool-call batch as downstream tools",
    "Run one Zotero search step, inspect its result",
    "stop the Zotero inspection chain immediately",
    "retry the query at most once",
    "not a downstream call pre-scheduled in the same tool-call batch",
]
SCHEDULED_TOOL_FAILURE_REQUIREMENTS = [
    "Scheduled Tool Failure Handling",
    "Tool skipped because a previous tool call in the scheduled sequence failed",
    "treat the skipped tool as **not executed**",
    "Identify and report the first failed tool in that scheduled sequence as the root cause",
    "rerun that specific upstream tool as a separate MCP call",
    "Never chain additional Zotero or PubMed dependent calls after a scheduled-sequence failure",
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
SENTENCE_CITATION_MATRIX_REQUIREMENTS = [
    "### SENTENCE_CITATION_MATRIX",
    "sentence_id",
    "Original sentence",
    "claim_ids",
    "citation_need",
    "Recommended citations",
    "Support verdict",
    "Evidence location",
    "Wording action",
    "Author check",
    "Create exactly one row per input sentence",
    "search-result snippet alone is insufficient",
]
CITATION_COVERAGE_SUMMARY_REQUIREMENTS = [
    "### CITATION_COVERAGE_SUMMARY",
    "Input sentences",
    "Sentences with `citation_required`",
    "Citation-required sentences covered",
    "Unmapped claims",
    "RIS candidates without a sentence/claim mapping",
    "Coverage status",
    "complete",
    "partial",
    "blocked",
    "not_applicable",
]
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
    module_15_pos = no_code.find("## 1.5 Collection and Tag Search")
    module_18_pos = no_code.find("## 1.8 Target Literature Search and Export")
    module_2_pos = no_code.find("## 2. Paragraph Evidence & Citation Analysis")
    if not (module_15_pos != -1 and module_15_pos < module_18_pos < module_2_pos):
        fail("Module 1.8 must appear after Module 1.5 and before Module 2")
    require_all(text, TARGET_LITERATURE_SEARCH_REQUIREMENTS, "target literature search requirement")
    require_all(text, TARGET_LITERATURE_CLASSIFICATION_REQUIREMENTS, "target literature classification requirement")
    require_all(text, SEARCH_RIS_REQUIREMENTS, "Search RIS requirement")
    require_all(text, PHASE2_TARGET_SEARCH_REQUIREMENTS, "Phase 2 target literature search quality requirement")
    require_all(text, PHASE3_LITERATURE_SEARCH_WRITER_REQUIREMENTS, "Phase 3 literature search writer requirement")
    ok("target literature search routing, classification, Search RIS, and Phase 2/3 quality requirements present")

    if not LITERATURE_SEARCH_WRITER_PATH.exists():
        fail(f"missing Phase 3 writer script: {LITERATURE_SEARCH_WRITER_PATH.relative_to(REPO_ROOT)}")
    writer_text = LITERATURE_SEARCH_WRITER_PATH.read_text(encoding="utf-8")
    require_all(writer_text, PHASE3_WRITER_SCRIPT_REQUIREMENTS, "Phase 3 writer script requirement")
    if not LITERATURE_SEARCH_WRITER_FIXTURE_PATH.exists():
        fail(f"missing Phase 3 writer fixture: {LITERATURE_SEARCH_WRITER_FIXTURE_PATH.relative_to(REPO_ROOT)}")
    try:
        fixture_data = json.loads(LITERATURE_SEARCH_WRITER_FIXTURE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Phase 3 writer fixture is not valid JSON: {exc}")
    if not isinstance(fixture_data, dict):
        fail("Phase 3 writer fixture must be a JSON object")
    missing_fixture_keys = [key for key in LITERATURE_SEARCH_WRITER_REQUIRED_TOP_LEVEL_KEYS if key not in fixture_data]
    if missing_fixture_keys:
        fail("Phase 3 writer fixture missing top-level key(s): " + ", ".join(missing_fixture_keys))
    ok("Phase 3 literature search writer script and fixture present")

    require_all(text, EVIDENCE_PACKAGE_REQUIREMENTS, "evidence package requirement")
    ok("evidence package export requirements present")

    require_all(text, SENTENCE_CITATION_MATRIX_REQUIREMENTS, "sentence-level citation matrix requirement")
    require_all(text, CITATION_COVERAGE_SUMMARY_REQUIREMENTS, "citation coverage summary requirement")
    ok("sentence-level citation matrix and coverage summary requirements present")

    require_all(text, ROUTE_CONTRACT_REQUIREMENTS, "route contract requirement")
    ok("single-owner route contract and handoff fields present")

    require_all(text, RECALL_FIRST_REQUIREMENTS, "recall-first retrieval and EndNote handoff requirement")
    ok("recall-first retrieval audit and EndNote handoff requirements present")

    require_all(text, ENDNOTE_COLLECTION_REQUIREMENTS, "section-aware EndNote collection requirement")
    ok("section-aware EndNote collection handoff requirements present")

    collection_writer = REPO_ROOT / "scripts" / "write_endnote_collection_package.py"
    if not collection_writer.exists():
        fail(f"missing section-aware EndNote collection writer: {collection_writer.relative_to(REPO_ROOT)}")
    collection_writer_text = collection_writer.read_text(encoding="utf-8")
    require_all(collection_writer_text, ("--ris", "--assignments", "--output-root", "--self-test", "Manuscript group:", "Unassigned/Unassigned", "master RIS once"), "section-aware EndNote collection writer")
    ok("section-aware EndNote collection writer present")

    recall_reference = REPO_ROOT / "zotero-evidence-review" / "references" / "recall-first-retrieval.md"
    if not recall_reference.exists():
        fail(f"missing recall-first retrieval reference: {recall_reference}")
    recall_text = recall_reference.read_text(encoding="utf-8")
    require_all(
        recall_text,
        (
            "zotero_semantic",
            "pubmed_broad",
            "saturated",
            "coverage_gaps",
            "ZOTERO_IMPORT_HANDOFF",
            "zotero_import_status",
            "zotero_add_by_doi",
            "zotero_update_search_database",
            "never invent a Zotero item key",
            "ENDNOTE_IMPORT_HANDOFF",
        ),
        "recall-first reference",
    )

    require_all(text, DEFAULT_EXPORT_REQUIREMENTS, "default export routing requirement")
    require_all(text, DUAL_MCP_AUTO_EXPORT_REQUIREMENTS, "Dual-MCP auto search/export default requirement")
    require_all(text, NUMBERED_CITATION_REPAIR_REQUIREMENTS, "numbered citation repair requirement")
    require_all(text, CITATION_SUPPORT_LEDGER_REQUIREMENTS, "Citation Support Ledger requirement")
    ok("default citation-support, Dual-MCP auto export, numbered-citation repair, and Citation Support Ledger routing requirements present")

    require_all(text, UNIFIED_WORKFLOW_REQUIREMENTS, "unified paragraph citation workflow requirement")
    ok("unified paragraph citation workflow requirements present")

    require_all(text, MCP_READINESS_REQUIREMENTS, "MCP readiness requirement")
    require_all(text, PUBMED_TOOL_REQUIREMENTS, "PubMed tool requirement")
    require_all(text, PUBMED_GUARDRAIL_REQUIREMENTS, "PubMed guardrail requirement")
    require_all(text, PUBMED_SEQUENTIAL_GUARDRAIL_REQUIREMENTS, "PubMed sequential execution guardrail")
    require_all(text, ZOTERO_SEQUENTIAL_GUARDRAIL_REQUIREMENTS, "Zotero sequential execution guardrail")
    require_all(text, SCHEDULED_TOOL_FAILURE_REQUIREMENTS, "scheduled tool failure handling guardrail")
    ok("MCP readiness, sequential execution, and scheduled-failure guardrail requirements present")

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

    literature_search_template = extract_template(text, "LITERATURE_SEARCH_REPORT")
    require_ordered(literature_search_template, LITERATURE_SEARCH_REPORT_SECTIONS, "Literature Search report section")
    require_table_header(
        literature_search_template,
        r"\| Field \| Value \|",
        ["Field", "Value"],
        "Literature Search task metadata",
    )
    require_table_header(
        literature_search_template,
        r"\| Decision \| Criteria \|",
        ["Decision", "Criteria"],
        "Literature Search inclusion/exclusion criteria",
    )
    require_table_header(
        literature_search_template,
        r"\| Component \| Value \|",
        ["Component", "Value"],
        "Literature Search topic decomposition",
    )
    require_table_header(
        literature_search_template,
        r"\| Query type \| Query \| Purpose \| Expected signal \| Noise-control note \|",
        ["Query type", "Query", "Purpose", "Expected signal", "Noise-control note"],
        "Literature Search query expansion plan",
    )
    require_table_header(
        literature_search_template,
        r"\| Category \| Include rule \| Exclude rule \| Default RIS action \|",
        ["Category", "Include rule", "Exclude rule", "Default RIS action"],
        "Literature Search classification standards",
    )
    require_table_header(
        literature_search_template,
        r"\| # \| Citation \| Year \| Category \| Role \| Zotero key \| DOI/PMID \| Why included \| Exclusion reason code \| RIS action \|",
        ["Citation", "Year", "Category", "Role", "Zotero key", "DOI/PMID", "Why included", "Exclusion reason code", "RIS action"],
        "Literature Search result table",
    )
    require_table_header(
        literature_search_template,
        r"\| Citation \| Category \| Exclusion reason code \| Human-readable reason \| RIS action \|",
        ["Citation", "Category", "Exclusion reason code", "Human-readable reason", "RIS action"],
        "Literature Search noise and exclusion reasons",
    )
    require_table_header(
        literature_search_template,
        r"\| Source \| Query \| Mode \| Max results \| Status \| Hits \| Included \| Notes \|",
        ["Source", "Query", "Mode", "Max results", "Status", "Hits", "Included", "Notes"],
        "Literature Search reproducibility",
    )
    require_table_header(
        literature_search_template,
        r"\| Citation \| DOI \| PMID \| PDF \| Missing metadata \| Duplicate / mismatch \| Evidence source \| RIS standardization source \| RIS action \|",
        ["Citation", "DOI", "PMID", "PDF", "Missing metadata", "Duplicate / mismatch", "Evidence source", "RIS standardization source", "RIS action"],
        "Literature Search metadata QC",
    )
    require_all(
        literature_search_template,
        [
            "Search mode | target_literature_search",
            "Status | Ready / Caution / Partial / Unknown",
            "Target object | {target object}",
            "Must-have concepts | {concepts required for Core classification}",
            "Negative / noise-control query",
            "Category` must use only `Core`, `Strong Related`, `Method Background`, `Disease GWAS Only`, `Noise`, or `Verify`",
            "Exclusion reason code` must use one of",
            "Search Reproducibility should include exact phrase or noise-control searches",
            "plain RIS only",
            "inspected metadata only",
            "PubMed status is `Completed` with inspected metadata",
            "relative paths only",
        ],
        "Literature Search report rule",
    )
    forbidden_literature_sections = [
        "## 4. 可直接使用的稿件文本（Copy-ready Manuscript Text）",
        "## 5. 注释版推荐文本（Annotated Recommended Text）",
        "Claim–Evidence Matrix）",
        "Citation Placement",
    ]
    found_forbidden = [section for section in forbidden_literature_sections if section in literature_search_template]
    if found_forbidden:
        fail("Literature Search report template contains paragraph evidence package section(s): " + ", ".join(found_forbidden))
    ok("Literature Search report template sections and tables present")

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
