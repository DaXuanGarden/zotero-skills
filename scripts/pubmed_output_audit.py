#!/usr/bin/env python3
"""Audit PubMed literature output packages.

The script scans generated PubMed review Markdown and RIS files for structural
traceability issues. It is read-only; it never writes package files.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "pubmed-literature-output"
STATUS_VALUES = ("Ready", "Caution", "Partial", "Unknown")
PUBMED_SECTIONS = (
    "Metadata and Use Status",
    "Critical Warnings",
    "Search Reproducibility",
    "Included Studies",
    "Related and Review Expansion",
    "Metadata Quality Control",
    "Export Files",
)
LEDGER_REQUIRED_TERMS = (
    "pmid",
    "citation",
    "inspection status",
    "inspection tool / route",
    "inspected fields",
    "doi",
    "abstract status",
    "retraction / metadata warning",
    "evidence use",
    "ris action",
)
SEARCH_REPRO_REQUIRED_TERMS = ("source", "query", "sort", "max results", "status", "hits reviewed", "selected pmids")
INCLUDED_STUDIES_REQUIRED_TERMS = ("priority", "citation", "pmid", "doi", "study type", "main finding/use", "caveat")
METADATA_QC_REQUIRED_TERMS = ("pmid", "doi", "title check", "authors check", "year check", "metadata warning", "ris action")
UNRESOLVED_WARNING_CUES = (
    "unresolved",
    "retracted",
    "retraction",
    "metadata conflict",
    "metadata mismatch",
    "possible mismatch",
)


@dataclass
class PubMedPackageAudit:
    folder: str
    md_file: str
    ris_file: str
    title: str
    generated: str
    status: str
    ris_exists: bool
    absolute_paths: list[str]
    section_order_ok: bool
    critical_warnings_present: bool
    search_repro_has_columns: bool
    included_studies_has_columns: bool
    pmid_ledger_present: bool
    pmid_ledger_has_columns: bool
    metadata_qc_has_columns: bool
    ledger_include_without_completed: list[str]
    ledger_include_search_snippet: list[str]
    ledger_include_warning: list[str]
    ledger_include_missing_pmid: list[str]
    ris_pmids_without_ledger_include: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit pubmed-literature-output packages; read-only")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="PubMed literature output directory")
    parser.add_argument("--fail-on-warnings", action="store_true", help="Exit non-zero when automated warnings are detected")
    parser.add_argument("--ignore-before", metavar="YYYY-MM-DD", help="Suppress warnings for output packages dated before this cutoff")
    return parser.parse_args()


def parse_cutoff(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise SystemExit(f"Invalid --ignore-before date {value!r}; expected YYYY-MM-DD") from exc


def extract_date(value: str) -> date | None:
    match = re.search(r"(20\d{2}-\d{2}-\d{2})", value)
    if not match:
        return None
    try:
        return date.fromisoformat(match.group(1))
    except ValueError:
        return None


def package_date(package: PubMedPackageAudit) -> date | None:
    return extract_date(package.folder) or extract_date(package.generated)


def is_historical_package(package: PubMedPackageAudit, cutoff: date | None) -> bool:
    package_day = package_date(package)
    return bool(cutoff and package_day and package_day < cutoff)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def first_match(pattern: str, text: str, default: str = "") -> str:
    match = re.search(pattern, text, flags=re.MULTILINE | re.IGNORECASE)
    return match.group(1).strip() if match else default


def find_main_markdown(folder: Path) -> Path | None:
    candidates = sorted(folder.glob("*_pubmed_review.md"))
    if candidates:
        return candidates[0]
    candidates = sorted(path for path in folder.glob("*.md") if path.name != "quick_use.md")
    return candidates[0] if candidates else None


def extract_generated(text: str) -> str:
    return first_match(r"^Generated:\s*(.+)$", text) or first_match(r"^生成日期：\s*(.+)$", text)


def infer_status(text: str) -> str:
    explicit = first_match(r"Status:\s*(Ready|Caution|Partial|Unknown)", text)
    if explicit in STATUS_VALUES:
        return explicit
    lowered = text.lower()
    if "pubmed status: completed" in lowered and "pmid inspection ledger" in lowered:
        return "Ready"
    if "failed" in lowered or "not executed" in lowered or "tool unavailable" in lowered:
        return "Partial"
    return "Unknown"


def split_markdown_table(lines: list[str]) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if cells and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(cells)
    return rows


def extract_section_lines(text: str, heading_pattern: str) -> list[str]:
    match = re.search(heading_pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    if not match:
        return []
    start = match.end()
    next_heading = re.search(r"^##\s+", text[start:], flags=re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end].splitlines()


def section_contains(text: str, heading_pattern: str) -> bool:
    return bool(extract_section_lines(text, heading_pattern))


def section_order_ok(text: str, sections: tuple[str, ...]) -> bool:
    position = -1
    for section in sections:
        match = re.search(rf"^##\s+.*{re.escape(section)}.*$", text, flags=re.MULTILINE | re.IGNORECASE)
        if not match or match.start() <= position:
            return False
        position = match.start()
    return True


def table_header_has(text: str, heading_pattern: str, required_terms: tuple[str, ...]) -> bool:
    lines = extract_section_lines(text, heading_pattern)
    rows = split_markdown_table(lines)
    if not rows:
        return False
    header = " | ".join(rows[0]).lower()
    return all(term in header for term in required_terms)


def pmid_ledger_rows(text: str) -> tuple[list[dict[str, str]], bool]:
    lines = extract_section_lines(text, r"^#{2,3}\s+.*PMID Inspection Ledger.*$")
    rows = split_markdown_table(lines)
    if not rows:
        return [], False
    header = [cell.strip() for cell in rows[0]]
    header_lc = " | ".join(cell.lower() for cell in header)
    has_required_columns = all(term in header_lc for term in LEDGER_REQUIRED_TERMS)
    output: list[dict[str, str]] = []
    for row in rows[1:]:
        item = {header[index]: row[index] if index < len(row) else "" for index in range(len(header))}
        if any(value.strip() for value in item.values()):
            output.append(item)
    return output, has_required_columns


def row_value(row: dict[str, str], column: str) -> str:
    return next((value for key, value in row.items() if key.lower() == column.lower()), "").strip()


def extract_ris_pmids(ris_text: str) -> set[str]:
    pmids = set(re.findall(r"^N1\s+-\s+PMID:\s*(\d+)", ris_text, flags=re.MULTILINE | re.IGNORECASE))
    pmids.update(re.findall(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)", ris_text, flags=re.IGNORECASE))
    return pmids


def ledger_semantic_findings(rows: list[dict[str, str]], ris_pmids: set[str]) -> tuple[list[str], list[str], list[str], list[str], list[str]]:
    include_without_completed: list[str] = []
    include_search_snippet: list[str] = []
    include_warning: list[str] = []
    include_missing_pmid: list[str] = []
    completed_include_pmids: set[str] = set()

    for index, row in enumerate(rows, start=1):
        pmid = row_value(row, "PMID")
        label = pmid or row_value(row, "Citation") or f"row {index}"
        inspection_status = row_value(row, "Inspection status").lower()
        route = row_value(row, "Inspection tool / route").lower()
        warning = row_value(row, "Retraction / metadata warning").lower()
        ris_action = row_value(row, "RIS action").lower()
        if ris_action != "include":
            continue
        if not pmid:
            include_missing_pmid.append(label)
        if inspection_status != "completed":
            include_without_completed.append(f"{label} ({inspection_status or 'missing status'})")
        if "search snippet" in route or "snippet only" in route:
            include_search_snippet.append(label)
        if any(cue in warning for cue in UNRESOLVED_WARNING_CUES):
            include_warning.append(f"{label} ({row_value(row, 'Retraction / metadata warning')})")
        if pmid and inspection_status == "completed":
            completed_include_pmids.add(pmid)

    ris_without_ledger = sorted(pmid for pmid in ris_pmids if pmid not in completed_include_pmids)
    return include_without_completed, include_search_snippet, include_warning, include_missing_pmid, ris_without_ledger


def audit_package(input_dir: Path, folder: Path) -> PubMedPackageAudit | None:
    md_path = find_main_markdown(folder)
    if md_path is None:
        return None
    text = read_text(md_path)
    ris_files = sorted(folder.glob("*.ris"))
    ris_file = ris_files[0].name if ris_files else ""
    ris_text = read_text(ris_files[0]) if ris_files else ""
    ledger_rows, ledger_has_columns = pmid_ledger_rows(text)
    findings = ledger_semantic_findings(ledger_rows, extract_ris_pmids(ris_text))
    return PubMedPackageAudit(
        folder=folder.name,
        md_file=md_path.name,
        ris_file=ris_file,
        title=first_match(r"^#\s+(.+)$", text, md_path.stem),
        generated=extract_generated(text),
        status=infer_status(text),
        ris_exists=bool(ris_files),
        absolute_paths=sorted(set(re.findall(r"(?:/Users/|/home/|/var/folders/|/tmp/)[^\s`)]+", text))),
        section_order_ok=section_order_ok(text, PUBMED_SECTIONS),
        critical_warnings_present=section_contains(text, r"^##\s+.*Critical Warnings.*$"),
        search_repro_has_columns=table_header_has(text, r"^##\s+.*Search Reproducibility.*$", SEARCH_REPRO_REQUIRED_TERMS),
        included_studies_has_columns=table_header_has(text, r"^##\s+.*Included Studies.*$", INCLUDED_STUDIES_REQUIRED_TERMS),
        pmid_ledger_present=section_contains(text, r"^#{2,3}\s+.*PMID Inspection Ledger.*$"),
        pmid_ledger_has_columns=ledger_has_columns,
        metadata_qc_has_columns=table_header_has(text, r"^#{2,3}\s+.*Metadata QC.*$", METADATA_QC_REQUIRED_TERMS),
        ledger_include_without_completed=findings[0],
        ledger_include_search_snippet=findings[1],
        ledger_include_warning=findings[2],
        ledger_include_missing_pmid=findings[3],
        ris_pmids_without_ledger_include=findings[4],
    )


def discover_packages(input_dir: Path) -> list[PubMedPackageAudit]:
    packages: list[PubMedPackageAudit] = []
    for folder in sorted(path for path in input_dir.iterdir() if path.is_dir()):
        package = audit_package(input_dir, folder)
        if package is not None:
            packages.append(package)
    return packages


def collect_warnings(packages: list[PubMedPackageAudit]) -> list[str]:
    warnings: list[str] = []
    for package in packages:
        if package.absolute_paths:
            warnings.append(f"{package.folder}: absolute paths found: {', '.join(package.absolute_paths)}")
        if not package.ris_exists:
            warnings.append(f"{package.folder}: package RIS file is missing")
        if package.status == "Unknown":
            warnings.append(f"{package.folder}: status could not be inferred")
        if not package.section_order_ok:
            warnings.append(f"{package.folder}: report sections do not match PubMed review order")
        if not package.critical_warnings_present:
            warnings.append(f"{package.folder}: missing Critical Warnings section")
        if not package.search_repro_has_columns:
            warnings.append(f"{package.folder}: Search Reproducibility table missing required columns")
        if not package.included_studies_has_columns:
            warnings.append(f"{package.folder}: Included Studies table missing required columns")
        if not package.pmid_ledger_present:
            warnings.append(f"{package.folder}: missing PMID Inspection Ledger section")
        elif not package.pmid_ledger_has_columns:
            warnings.append(f"{package.folder}: PMID Inspection Ledger missing required columns")
        if not package.metadata_qc_has_columns:
            warnings.append(f"{package.folder}: Metadata QC table missing required columns")
        if package.ledger_include_without_completed:
            warnings.append(
                f"{package.folder}: RIS include rows without completed inspection: "
                + ", ".join(package.ledger_include_without_completed)
            )
        if package.ledger_include_search_snippet:
            warnings.append(
                f"{package.folder}: RIS include rows use search-snippet-only routes: "
                + ", ".join(package.ledger_include_search_snippet)
            )
        if package.ledger_include_warning:
            warnings.append(
                f"{package.folder}: RIS include rows have unresolved retraction/metadata warnings: "
                + ", ".join(package.ledger_include_warning)
            )
        if package.ledger_include_missing_pmid:
            warnings.append(
                f"{package.folder}: RIS include rows are missing PMID: "
                + ", ".join(package.ledger_include_missing_pmid)
            )
        if package.ris_pmids_without_ledger_include:
            warnings.append(
                f"{package.folder}: RIS PMIDs lack completed/include PMID Inspection Ledger rows: "
                + ", ".join(package.ris_pmids_without_ledger_include)
            )
    return warnings


def print_report(packages: list[PubMedPackageAudit]) -> None:
    print(f"Scanned PubMed packages: {len(packages)}")
    for package in packages:
        ris_state = "ok" if package.ris_exists else "missing"
        print(f"- {package.folder}: {package.status} ({ris_state})")
    warnings = collect_warnings(packages)
    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"- {warning}")
    else:
        print("\nNo automated warnings detected.")


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input)
    if not input_dir.is_absolute():
        input_dir = REPO_ROOT / input_dir
    if not input_dir.exists():
        raise SystemExit(f"Input directory does not exist: {input_dir}")

    packages = discover_packages(input_dir)
    print_report(packages)

    cutoff = parse_cutoff(args.ignore_before)
    warnings = collect_warnings(packages)
    if cutoff:
        historical_folders = {package.folder for package in packages if is_historical_package(package, cutoff)}
        active_warnings = [warning for warning in warnings if warning.split(":", 1)[0] not in historical_folders]
        suppressed_count = len(warnings) - len(active_warnings)
        print(f"\nHistorical warning cutoff: suppressing {suppressed_count} warning(s) from packages before {cutoff.isoformat()}.")
    else:
        active_warnings = warnings

    print("\nRead-only audit: no output files written.")

    if args.fail_on_warnings and active_warnings:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
