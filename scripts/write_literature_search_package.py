#!/usr/bin/env python3
"""Write target literature search Markdown and RIS packages from inspected metadata.

CLI: scripts/write_literature_search_package.py.

This script does not search Zotero or PubMed. It only formats candidate records
that were already searched, classified, and metadata-inspected by the workflow.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import tempfile
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - optional dependency only
    yaml = None

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "zotero-evidence-output"
SAMPLE_FIXTURE = REPO_ROOT / "scripts" / "fixtures" / "literature_search_package_sample.json"

REQUIRED_TOP_LEVEL_KEYS = (
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
ALLOWED_CATEGORIES = (
    "Core",
    "Strong Related",
    "Method Background",
    "Disease GWAS Only",
    "Noise",
    "Verify",
)
ALLOWED_RIS_ACTIONS = ("Include", "Optional", "Exclude", "Verify")
ALLOWED_EXCLUSION_CODES = (
    "wrong data layer",
    "disease-only GWAS",
    "method-only",
    "generic catalog",
    "metadata insufficient",
    "duplicate",
    "off-topic",
    "wrong population",
    "no inspected metadata",
    "none",
)
RIS_INCLUDE_CATEGORIES = {"Core", "Strong Related"}
RIS_OPTIONAL_CATEGORIES = {"Core", "Strong Related", "Method Background"}
ITEM_TYPE_MAP = {
    "journalArticle": "JOUR",
    "journal article": "JOUR",
    "article": "JOUR",
    "book": "BOOK",
    "conferencePaper": "CONF",
    "conference paper": "CONF",
    "preprint": "UNPB",
    "report": "RPRT",
    "thesis": "THES",
    "webpage": "ELEC",
    "bookSection": "CHAP",
    "book section": "CHAP",
    "dataset": "DATA",
    "patent": "PAT",
}
REPORT_SECTIONS = (
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
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Write a target literature search Markdown report and Search RIS from JSON/YAML candidate metadata."
    )
    parser.add_argument("--input", help="Input JSON/YAML file containing inspected target literature search candidates")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT), help="Output root directory")
    parser.add_argument("--slug", help="Brief topic slug; inferred from run.topic when omitted")
    parser.add_argument("--timestamp", help="Timestamp suffix in YYYY-MM-DD_HHMMSS format")
    parser.add_argument("--include-optional", action="store_true", help="Include RIS action = Optional records when eligible")
    parser.add_argument("--no-ris", action="store_true", help="Write only the Markdown literature search report")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print planned paths without writing files")
    parser.add_argument("--self-test", action="store_true", help="Run a temporary fixture-based self-test and exit")
    return parser.parse_args()


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def load_payload(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"input file does not exist: {path}")
    suffix = path.suffix.lower()
    text = path.read_text(encoding="utf-8")
    if suffix == ".json":
        data = json.loads(text)
    elif suffix in {".yaml", ".yml"}:
        if yaml is None:
            fail("YAML input requires PyYAML to be installed; JSON input is always supported and no new dependency is added")
        data = yaml.safe_load(text)
    else:
        fail("input must be .json, .yaml, or .yml")
    if not isinstance(data, dict):
        fail("input root must be a JSON/YAML object")
    return data


def as_dict(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{context} must be an object")
    return value


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def stringify(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (list, tuple)):
        return "; ".join(stringify(item, default="") for item in value if stringify(item, default=""))
    return str(value)


def first_value(mapping: dict[str, Any], *keys: str, default: str = "") -> str:
    for key in keys:
        value = mapping.get(key)
        if value not in (None, ""):
            return stringify(value)
    return default


def bool_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "y", "1", "completed", "inspected"}
    return bool(value)


def table_cell(value: Any, default: str = "none") -> str:
    text = stringify(value, default=default).strip() or default
    return text.replace("\n", "<br>").replace("|", "\\|")


def bullet_text(value: Any) -> list[str]:
    items = [stringify(item).strip() for item in as_list(value)]
    return [item for item in items if item]


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    normalized = normalized.lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized[:80].strip("_") or "literature_search"


def validate_timestamp(value: str) -> str:
    try:
        datetime.strptime(value, "%Y-%m-%d_%H%M%S")
    except ValueError as exc:
        fail(f"invalid --timestamp {value!r}; expected YYYY-MM-DD_HHMMSS")
    return value


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return os.path.relpath(path, REPO_ROOT)


def output_paths(output_root: Path, slug: str, timestamp: str) -> dict[str, Path]:
    run_stem = f"{slug}_{timestamp}"
    base = output_root / run_stem
    run_dir = base
    version = 2
    while run_dir.exists():
        run_dir = output_root / f"{run_stem}_v{version}"
        version += 1
    file_stem = run_dir.name
    return {
        "run_dir": run_dir,
        "markdown": run_dir / f"{file_stem}_literature_search.md",
        "ris": run_dir / f"{file_stem}_references.ris",
    }


def validate_payload(data: dict[str, Any]) -> None:
    missing = [key for key in REQUIRED_TOP_LEVEL_KEYS if key not in data]
    if missing:
        fail("input missing required top-level key(s): " + ", ".join(missing))
    as_dict(data["run"], "run")
    as_dict(data["topic_decomposition"], "topic_decomposition")
    candidates = data["candidates"]
    if not isinstance(candidates, list):
        fail("candidates must be a list")
    if not candidates:
        fail("candidates must contain at least one record")
    for index, candidate in enumerate(candidates, start=1):
        if not isinstance(candidate, dict):
            fail(f"candidates[{index}] must be an object")
        category = first_value(candidate, "category")
        if category not in ALLOWED_CATEGORIES:
            fail(f"candidates[{index}].category must be one of {', '.join(ALLOWED_CATEGORIES)}")
        ris_action = first_value(candidate, "ris_action")
        if ris_action not in ALLOWED_RIS_ACTIONS:
            fail(f"candidates[{index}].ris_action must be one of {', '.join(ALLOWED_RIS_ACTIONS)}")
        reason_code = first_value(candidate, "exclusion_reason_code", default="none")
        if reason_code not in ALLOWED_EXCLUSION_CODES:
            fail(f"candidates[{index}].exclusion_reason_code must be one of {', '.join(ALLOWED_EXCLUSION_CODES)}")
        if ris_action == "Include" and category not in RIS_INCLUDE_CATEGORIES:
            fail(f"candidates[{index}] uses RIS action Include with non-eligible category {category!r}")


def candidate_source(candidate: dict[str, Any]) -> str:
    return first_value(candidate, "evidence_source", "source", default="Zotero")


def is_pubmed_only(candidate: dict[str, Any]) -> bool:
    source = candidate_source(candidate).strip().lower()
    zotero_key = first_value(candidate, "zotero_key")
    return source == "pubmed" or (source == "pubmed-only") or zotero_key == "PubMed-only"


def selected_ris_candidates(data: dict[str, Any], include_optional: bool) -> list[dict[str, Any]]:
    run = as_dict(data["run"], "run")
    selected: list[dict[str, Any]] = []
    for index, candidate in enumerate(data["candidates"], start=1):
        action = first_value(candidate, "ris_action")
        category = first_value(candidate, "category")
        include = action == "Include" and category in RIS_INCLUDE_CATEGORIES
        include = include or (
            include_optional and action == "Optional" and category in RIS_OPTIONAL_CATEGORIES
        )
        if not include:
            continue
        if not bool_value(candidate.get("metadata_inspected")):
            fail(f"candidates[{index}] is selected for RIS but metadata_inspected is not true")
        if is_pubmed_only(candidate):
            pubmed_status = first_value(candidate, "pubmed_status", default=first_value(run, "pubmed_status"))
            if pubmed_status != "Completed":
                fail(f"candidates[{index}] is PubMed-only but pubmed_status is not Completed")
        selected.append(candidate)
    return selected


def format_author(author: Any) -> str:
    if isinstance(author, str):
        return author.strip()
    if isinstance(author, dict):
        name = first_value(author, "name", "full_name", "fullName")
        if name:
            return name
        last = first_value(author, "lastName", "last", "family")
        first = first_value(author, "firstName", "first", "given")
        if last and first:
            return f"{last}, {first}"
        return last or first
    return stringify(author)


def ris_record_data(candidate: dict[str, Any]) -> dict[str, Any]:
    nested = candidate.get("ris")
    data = nested.copy() if isinstance(nested, dict) else {}
    for key, value in candidate.items():
        data.setdefault(key, value)
    return data


def filtered_tags(tags: Any) -> list[str]:
    output: list[str] = []
    for tag in as_list(tags):
        text = stringify(tag).strip()
        lowered = text.lower()
        if not text or text.startswith("/"):
            continue
        if not re.search(r"[A-Za-z0-9\u4e00-\u9fff]", text):
            continue
        if lowered in {"todo", "read", "unread", "to read", "done", "reading", "已读", "待读"}:
            continue
        output.append(text)
    return output


def split_pages(pages: str) -> tuple[str, str]:
    if not pages:
        return "", ""
    match = re.match(r"^\s*([A-Za-z]?\d+\w*)\s*[-–—]\s*([A-Za-z]?\d+\w*)\s*$", pages)
    if match:
        return match.group(1), match.group(2)
    return pages, ""


def write_ris_record(candidate: dict[str, Any]) -> str:
    data = ris_record_data(candidate)
    lines: list[str] = []

    def add(tag: str, value: Any) -> None:
        for item in as_list(value):
            text = stringify(item).strip()
            if text:
                lines.append(f"{tag}  - {text}")

    item_type = first_value(data, "type", "item_type", "itemType", default="JOUR")
    ris_type = ITEM_TYPE_MAP.get(item_type, ITEM_TYPE_MAP.get(item_type.lower(), item_type.upper()))
    if len(ris_type) > 4:
        ris_type = "JOUR"
    add("TY", ris_type)
    for author in as_list(data.get("authors") or data.get("creators")):
        formatted = format_author(author)
        if formatted:
            add("AU", formatted)
    year = first_value(data, "year", "publication_year")
    add("PY", year)
    add("Y1", first_value(data, "date", "publication_date"))
    add("TI", first_value(data, "title"))
    add("JO", first_value(data, "journal", "publicationTitle", "publication_title"))
    add("J2", first_value(data, "journal_abbreviation", "journalAbbreviation"))
    add("VL", first_value(data, "volume"))
    add("IS", first_value(data, "issue"))
    start_page, end_page = split_pages(first_value(data, "pages"))
    add("SP", start_page)
    add("EP", end_page)
    doi = first_value(data, "doi", "DOI")
    pmid = first_value(data, "pmid", "PMID")
    url = first_value(data, "url")
    add("DO", doi)
    add("AN", pmid)
    if not url and doi:
        url = f"https://doi.org/{doi}"
    if not url and pmid:
        url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
    add("UR", url)
    add("AB", first_value(data, "abstract", "abstractNote"))
    add("LA", first_value(data, "language"))
    for keyword in filtered_tags(data.get("keywords") or data.get("tags")):
        add("KW", keyword)
    zotero_key = first_value(data, "zotero_key", "key")
    if zotero_key and zotero_key != "PubMed-only":
        add("N1", f"Zotero key: {zotero_key}")
    elif pmid:
        add("N1", f"PMID: {pmid}")
    lines.append("ER  -")
    return "\n".join(lines)


def build_ris(candidates: list[dict[str, Any]]) -> str:
    records = [write_ris_record(candidate) for candidate in candidates]
    text = "\n\n".join(records).rstrip() + "\n"
    validate_ris_text(text)
    return text


def validate_ris_text(text: str) -> None:
    if re.search(r"^#{1,6}\s", text, flags=re.MULTILINE) or "```" in text:
        fail("generated RIS contains Markdown")
    records = [record for record in re.split(r"\n\s*\n", text.strip()) if record.strip()]
    if not records:
        fail("generated RIS contains no records")
    for index, record in enumerate(records, start=1):
        lines = [line for line in record.splitlines() if line.strip()]
        if not lines[0].startswith("TY  -"):
            fail(f"RIS record {index} does not start with TY  -")
        if not lines[-1].startswith("ER  -"):
            fail(f"RIS record {index} does not end with ER  -")


def rows_from_mapping_or_list(value: Any, key_name: str, value_name: str) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        return [{key_name: key, value_name: item} for key, item in value.items()]
    rows = []
    for item in as_list(value):
        if isinstance(item, dict):
            rows.append(item)
        else:
            rows.append({key_name: "", value_name: item})
    return rows


def render_query_rows(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        rows = []
        aliases = [
            ("Semantic query", "semantic_query"),
            ("Keyword query", "keyword_query"),
            ("Exact phrase query", "exact_phrase_query"),
            ("Negative / noise-control query", "negative_noise_control_query"),
        ]
        for label, key in aliases:
            raw = value.get(key)
            if raw is None:
                continue
            rows.append(
                {
                    "query_type": label,
                    "query": raw,
                    "purpose": value.get(f"{key}_purpose", ""),
                    "expected_signal": value.get(f"{key}_expected_signal", ""),
                    "noise_control_note": value.get(f"{key}_noise_control_note", ""),
                }
            )
        return rows
    return [item for item in as_list(value) if isinstance(item, dict)]


def render_report(
    data: dict[str, Any],
    paths: dict[str, Path],
    timestamp: str,
    selected_count: int,
    ris_requested: bool,
) -> str:
    run = as_dict(data["run"], "run")
    topic = first_value(run, "topic", default="target literature search")
    search_date = first_value(run, "search_date", default=timestamp.split("_", 1)[0])
    output_mode = "Search Report + RIS" if ris_requested else "Search Report"
    critical_warnings = bullet_text(data.get("critical_warnings")) or ["No critical warnings"]
    lines: list[str] = [f"# 文献检索报告：{topic}", ""]

    lines.extend(
        [
            "## 1. 检索任务",
            "| Field | Value |",
            "|---|---|",
            f"| Topic | {table_cell(topic)} |",
            f"| User question | {table_cell(first_value(run, 'user_question', 'question', default=topic))} |",
            f"| Search date | {table_cell(search_date)} |",
            "| Search mode | target_literature_search |",
            f"| Zotero status | {table_cell(first_value(run, 'zotero_status', default='Not executed'))} |",
            f"| PubMed status | {table_cell(first_value(run, 'pubmed_status', default='Not executed'))} |",
            f"| Output | {table_cell(first_value(run, 'output', default=output_mode))} |",
            f"| Status | {table_cell(first_value(run, 'status', default='Unknown'))} |",
            f"| Status rationale | {table_cell(first_value(run, 'status_rationale', default='Generated from supplied inspected candidate metadata.'))} |",
            "",
        ]
    )

    decomposition = as_dict(data["topic_decomposition"], "topic_decomposition")
    lines.extend(
        [
            "## 2. Topic Decomposition",
            "| Component | Value |",
            "|---|---|",
            f"| Target object | {table_cell(first_value(decomposition, 'target_object'))} |",
            f"| Data / method / phenotype / cohort | {table_cell(first_value(decomposition, 'data_method_phenotype_cohort', 'data_method_phenotype_or_cohort'))} |",
            f"| Must-have concepts | {table_cell(first_value(decomposition, 'must_have_concepts'))} |",
            f"| Adjacent concepts | {table_cell(first_value(decomposition, 'adjacent_concepts'))} |",
            f"| Exclusion concepts | {table_cell(first_value(decomposition, 'exclusion_concepts'))} |",
            f"| Time / source constraints | {table_cell(first_value(decomposition, 'time_source_constraints'))} |",
            "",
            "## 3. Query Expansion Plan",
            "| Query type | Query | Purpose | Expected signal | Noise-control note |",
            "|---|---|---|---|---|",
        ]
    )
    query_rows = render_query_rows(data["query_expansion"])
    for row in query_rows:
        lines.append(
            "| {query_type} | {query} | {purpose} | {expected_signal} | {noise_control_note} |".format(
                query_type=table_cell(first_value(row, "query_type", "type")),
                query=table_cell(first_value(row, "query")),
                purpose=table_cell(first_value(row, "purpose")),
                expected_signal=table_cell(first_value(row, "expected_signal")),
                noise_control_note=table_cell(first_value(row, "noise_control_note", "noise_control")),
            )
        )
    if not query_rows:
        lines.append("| Not recorded | Not recorded | Not recorded | Not recorded | Not recorded |")
    lines.append("")

    lines.extend(["## 4. 纳入与排除标准", "| Decision | Criteria |", "|---|---|"])
    for row in rows_from_mapping_or_list(data["criteria"], "decision", "criteria"):
        lines.append(f"| {table_cell(first_value(row, 'decision', 'Decision'))} | {table_cell(first_value(row, 'criteria', 'Criteria'))} |")
    lines.append("")

    lines.extend(
        [
            "## 5. 结果分类标准",
            "| Category | Include rule | Exclude rule | Default RIS action |",
            "|---|---|---|---|",
            "| Core | Directly uses the requested target data/method/phenotype/cohort/resource | Exclude if target use is only inferred from a vague title | Include |",
            "| Strong Related | Explicitly uses adjacent evidence useful for the target set | Exclude if relation is only a shared disease label or generic method | Include / Optional |",
            "| Method Background | Important method/context paper without direct target use | Exclude from Search RIS unless background methods were requested | Optional / Exclude |",
            "| Disease GWAS Only | Disease or psychiatric GWAS without requested data/method/phenotype layer | Exclude from target data/method literature set | Exclude |",
            "| Noise | Off-topic, wrong data layer, generic catalog, duplicate, wrong population, or unrelated retrieval | Exclude and record reason code | Exclude |",
            "| Verify | Possible relevance but metadata/abstract/full text is insufficient | Exclude from RIS until verified unless user overrides | Verify |",
            "",
            "## 6. 核心发现",
        ]
    )
    findings = bullet_text(data["findings"])
    lines.extend([f"- {finding}" for finding in findings] or ["- No findings recorded."])
    lines.append("")

    candidates = data["candidates"]
    lines.extend(
        [
            "## 7. 检索结果总表",
            "| # | Citation | Year | Category | Role | Zotero key | DOI/PMID | Why included | Exclusion reason code | RIS action |",
            "|---|----------|------|----------|------|------------|----------|--------------|-----------------------|------------|",
        ]
    )
    for index, candidate in enumerate(candidates, start=1):
        doi_pmid = first_value(candidate, "doi", "DOI") or first_value(candidate, "pmid", "PMID") or "none"
        lines.append(
            f"| {index} | {table_cell(first_value(candidate, 'citation'))} | {table_cell(first_value(candidate, 'year'))} | "
            f"{table_cell(first_value(candidate, 'category'))} | {table_cell(first_value(candidate, 'role'))} | "
            f"{table_cell(first_value(candidate, 'zotero_key', default='PubMed-only' if is_pubmed_only(candidate) else 'none'))} | "
            f"{table_cell(doi_pmid)} | {table_cell(first_value(candidate, 'why_included'))} | "
            f"{table_cell(first_value(candidate, 'exclusion_reason_code', default='none'))} | {table_cell(first_value(candidate, 'ris_action'))} |"
        )
    lines.append("")

    lines.extend(["## 8. 分类结果", "### Core", "| Citation | Data / method used | Why core |", "|----------|--------------------|----------|"])
    for candidate in [item for item in candidates if item["category"] == "Core"]:
        lines.append(f"| {table_cell(first_value(candidate, 'citation'))} | {table_cell(first_value(candidate, 'data_method_used', 'role'))} | {table_cell(first_value(candidate, 'why_core', 'why_included'))} |")
    lines.extend(["", "### Strong Related", "| Citation | Relation | Why related |", "|----------|----------|-------------|"])
    for candidate in [item for item in candidates if item["category"] == "Strong Related"]:
        lines.append(f"| {table_cell(first_value(candidate, 'citation'))} | {table_cell(first_value(candidate, 'relation', 'role'))} | {table_cell(first_value(candidate, 'why_related', 'why_included'))} |")
    lines.extend(["", "### Method Background", "| Citation | Method role | RIS action |", "|----------|-------------|------------|"])
    for candidate in [item for item in candidates if item["category"] == "Method Background"]:
        lines.append(f"| {table_cell(first_value(candidate, 'citation'))} | {table_cell(first_value(candidate, 'method_role', 'role'))} | {table_cell(first_value(candidate, 'ris_action'))} |")
    lines.extend(["", "### Disease GWAS Only / Noise / Verify", "| Citation | Category | Reason | RIS action |", "|----------|----------|--------|------------|"])
    for candidate in [item for item in candidates if item["category"] in {"Disease GWAS Only", "Noise", "Verify"}]:
        lines.append(f"| {table_cell(first_value(candidate, 'citation'))} | {table_cell(first_value(candidate, 'category'))} | {table_cell(first_value(candidate, 'reason', 'why_included'))} | {table_cell(first_value(candidate, 'ris_action'))} |")
    lines.append("")

    lines.extend(
        [
            "## 9. 噪音与排除原因",
            "| Citation | Category | Exclusion reason code | Human-readable reason | RIS action |",
            "|----------|----------|-----------------------|-----------------------|------------|",
        ]
    )
    excluded = [
        item for item in candidates
        if item["ris_action"] in {"Exclude", "Verify"} or item["category"] in {"Method Background", "Disease GWAS Only", "Noise", "Verify"}
    ]
    for candidate in excluded:
        lines.append(
            f"| {table_cell(first_value(candidate, 'citation'))} | {table_cell(first_value(candidate, 'category'))} | "
            f"{table_cell(first_value(candidate, 'exclusion_reason_code', default='none'))} | {table_cell(first_value(candidate, 'reason', 'why_included'))} | "
            f"{table_cell(first_value(candidate, 'ris_action'))} |"
        )
    if not excluded:
        lines.append("| none | none | none | none | none |")
    lines.append("")

    lines.extend(["## 10. 推荐阅读顺序", "| Priority | Citation | Why read first |", "|----------|----------|----------------|"])
    for row in as_list(data["reading_order"]):
        if isinstance(row, dict):
            lines.append(f"| {table_cell(first_value(row, 'priority'))} | {table_cell(first_value(row, 'citation'))} | {table_cell(first_value(row, 'why_read_first', 'why'))} |")
    lines.append("")

    lines.extend(
        [
            "## 11. Search Reproducibility",
            "| Source | Query | Mode | Max results | Status | Hits | Included | Notes |",
            "|---|---|---|---:|---|---:|---:|---|",
        ]
    )
    for row in as_list(data["reproducibility"]):
        if not isinstance(row, dict):
            continue
        lines.append(
            f"| {table_cell(first_value(row, 'source'))} | {table_cell(first_value(row, 'query'))} | {table_cell(first_value(row, 'mode'))} | "
            f"{table_cell(first_value(row, 'max_results', default='Not recorded'))} | {table_cell(first_value(row, 'status'))} | "
            f"{table_cell(first_value(row, 'hits', default='0'))} | {table_cell(first_value(row, 'included', 'included_count', default='0'))} | "
            f"{table_cell(first_value(row, 'notes'))} |"
        )
    lines.append("")

    lines.extend(
        [
            "## 12. Metadata QC",
            "| Citation | DOI | PMID | PDF | Missing metadata | Duplicate / mismatch | Evidence source | RIS standardization source | RIS action |",
            "|----------|-----|------|-----|------------------|----------------------|-----------------|----------------------------|------------|",
        ]
    )
    for candidate in candidates:
        lines.append(
            f"| {table_cell(first_value(candidate, 'citation'))} | {table_cell(first_value(candidate, 'doi', 'DOI', default='missing'))} | "
            f"{table_cell(first_value(candidate, 'pmid', 'PMID', default='missing'))} | {table_cell(first_value(candidate, 'pdf', default='-'))} | "
            f"{table_cell(first_value(candidate, 'missing_metadata', default='none'))} | {table_cell(first_value(candidate, 'duplicate_mismatch', default='none'))} | "
            f"{table_cell(candidate_source(candidate))} | {table_cell(first_value(candidate, 'ris_standardization_source', default='Zotero metadata'))} | "
            f"{table_cell(first_value(candidate, 'ris_action'))} |"
        )
    lines.append("")

    md_path = relative(paths["markdown"])
    ris_path = relative(paths["ris"]) if ris_requested else "Not requested"
    lines.extend(
        [
            "## 13. Export Files",
            f"- Markdown report: `{md_path}`",
            f"- EndNote RIS: `{ris_path}`",
            f"- Included records: {selected_count}",
            "- Search RIS rule: selected literature set only; Core included by default; Strong Related included only when explicitly marked Include/Optional; Method Background, Disease GWAS Only, Noise, and unresolved Verify excluded by default.",
            "- Critical warnings: " + "; ".join(critical_warnings),
            "",
        ]
    )
    return "\n".join(lines)


def assert_report_shape(markdown: str) -> None:
    for section in REPORT_SECTIONS:
        if section not in markdown:
            fail(f"generated Markdown missing section: {section}")
    forbidden = ("Copy-ready Manuscript Text", "Claim–Evidence Matrix", "Citation Placement")
    for phrase in forbidden:
        if phrase in markdown:
            fail(f"generated literature search Markdown contains paragraph package phrase: {phrase}")


def write_package(
    data: dict[str, Any],
    output_root: Path,
    slug: str,
    timestamp: str,
    include_optional: bool,
    no_ris: bool,
    dry_run: bool,
) -> dict[str, Any]:
    validate_payload(data)
    selected = selected_ris_candidates(data, include_optional)
    if not no_ris and not selected:
        fail("no eligible records for RIS; use --no-ris or mark inspected Core/Strong Related records as Include")
    paths = output_paths(output_root, slug, timestamp)
    markdown = render_report(data, paths, timestamp, len(selected), not no_ris)
    assert_report_shape(markdown)
    ris_text = "" if no_ris else build_ris(selected)
    if dry_run:
        return {"paths": paths, "markdown": markdown, "ris": ris_text, "selected_count": len(selected), "written": False}
    paths["run_dir"].mkdir(parents=True, exist_ok=False)
    paths["markdown"].write_text(markdown, encoding="utf-8")
    if not no_ris:
        paths["ris"].write_text(ris_text, encoding="utf-8")
    return {"paths": paths, "markdown": markdown, "ris": ris_text, "selected_count": len(selected), "written": True}


def run_self_test() -> None:
    if not SAMPLE_FIXTURE.exists():
        fail(f"self-test fixture missing: {SAMPLE_FIXTURE}")
    temp_root = Path(tempfile.mkdtemp(prefix="zotero-lit-writer-"))
    try:
        data = load_payload(SAMPLE_FIXTURE)
        timestamp = "2026-07-07_120000"
        result = write_package(
            data=data,
            output_root=temp_root,
            slug="brain_gwas",
            timestamp=timestamp,
            include_optional=False,
            no_ris=False,
            dry_run=False,
        )
        md_path = result["paths"]["markdown"]
        ris_path = result["paths"]["ris"]
        if not md_path.exists() or not ris_path.exists():
            fail("self-test did not write expected Markdown and RIS files")
        validate_ris_text(ris_path.read_text(encoding="utf-8"))
        assert_report_shape(md_path.read_text(encoding="utf-8"))
        print("Self-test passed.")
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def main() -> None:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return
    if not args.input:
        fail("--input is required unless --self-test is used")
    data = load_payload(Path(args.input))
    run = as_dict(data.get("run", {}), "run")
    timestamp = validate_timestamp(args.timestamp) if args.timestamp else datetime.now().strftime("%Y-%m-%d_%H%M%S")
    slug = slugify(args.slug or first_value(run, "slug", "topic", default="literature_search"))
    output_root = Path(args.output_root)
    if not output_root.is_absolute():
        output_root = REPO_ROOT / output_root
    result = write_package(
        data=data,
        output_root=output_root,
        slug=slug,
        timestamp=timestamp,
        include_optional=args.include_optional,
        no_ris=args.no_ris,
        dry_run=args.dry_run,
    )
    paths = result["paths"]
    action = "Would write" if args.dry_run else "Wrote"
    print(f"{action} literature search package:")
    print(f"- Markdown report: {relative(paths['markdown'])}")
    if args.no_ris:
        print("- EndNote RIS: Not requested")
    else:
        print(f"- EndNote RIS: {relative(paths['ris'])}")
    print(f"- Included records: {result['selected_count']}")


if __name__ == "__main__":
    main()
