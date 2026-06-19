#!/usr/bin/env python3
"""Audit Zotero evidence output packages.

The script scans evidence-review Markdown and RIS files, reports common QA
issues, and writes draft project-level summary/TSV files. It does not modify
source reports.
"""

from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPO_ROOT / "zotero-evidence-output"
STATUS_VALUES = ("Ready", "Caution", "Partial", "Superseded", "Unknown")
PARTIAL_CUES = (
    "pubmed query failed",
    "too many requests",
    "tool unavailable",
    "search failed",
    "pmos concept not verified",
    "pmos source: unresolved",
)
CAUTION_CUES = (
    "no direct evidence",
    "not directly established",
    "does not directly",
    "not established",
    "unsupported",
    "malformed",
    "duplicate",
    "not externally",
    "requires verification",
    "reviewer risk",
)
HIGH_RISK_CUES = (
    "no direct evidence",
    "pubmed query failed",
    "citation not verified",
    "metadata malformed",
    "duplicate zotero",
    "too many requests",
    "pmos",
    "horizontal pleiotropy",
    "bmi-independent",
    "cerebellar",
)
MANUAL_STATUS_OVERRIDES = {
    "sedentary_behavior_pcos_2026-06-19_020100": "Ready",
}
PHASE10_SECTIONS = (
    "Metadata and Use Status",
    "Critical Warnings",
    "核心结论",
    "Copy-ready Manuscript Text",
    "Annotated Recommended Text",
    "Claim–Evidence Matrix",
    "Citation Placement",
    "Evidence Logic Chain",
    "Reference Table",
    "Search Reproducibility",
    "Zotero Search Summary",
    "PubMed Expansion",
    "Integrated Writing Advice",
    "Claims to Revise or Remove",
    "Gaps and Reviewer-risk Assessment",
    "Metadata Quality Control",
    "Export File",
)


@dataclass
class PackageAudit:
    folder: str
    md_file: str
    ris_file: str
    title: str
    generated: str
    status: str
    main_risk: str
    ris_exists: bool
    absolute_paths: list[str]
    declared_ris_paths: list[str]
    reference_rows: list[dict[str, str]]
    claim_rows: list[dict[str, str]]
    critical_warnings_present: bool
    copy_ready_present: bool
    claim_matrix_has_evidence_level: bool
    claim_matrix_has_source_layer: bool
    claim_matrix_has_recommended_action: bool
    claim_matrix_has_recommended_citation: bool
    evidence_logic_chain_present: bool
    claims_to_revise_present: bool
    reference_canonicalization_present: bool
    phase10_section_order_ok: bool
    ris_markdown_artifacts: list[str]
    unresolved_mismatch_mentions: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit zotero-evidence-output packages")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Evidence output directory")
    parser.add_argument("--write-summary", action="store_true", help="Write PROJECT_SUMMARY.draft.md")
    parser.add_argument("--write-claims", action="store_true", help="Write evidence_claims_master.draft.tsv")
    parser.add_argument("--write-reference-qc", action="store_true", help="Write reference_qc_master.draft.tsv")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def first_match(pattern: str, text: str, default: str = "") -> str:
    match = re.search(pattern, text, flags=re.MULTILINE | re.IGNORECASE)
    return match.group(1).strip() if match else default


def find_main_markdown(folder: Path) -> Path | None:
    candidates = sorted(folder.glob("*_evidence_review.md"))
    if candidates:
        return candidates[0]
    candidates = sorted(path for path in folder.glob("*.md") if path.name != "quick_use.md")
    return candidates[0] if candidates else None


def extract_generated(text: str) -> str:
    return first_match(r"^Generated:\s*(.+)$", text) or first_match(r"^生成日期：\s*(.+)$", text)


def extract_declared_ris_paths(text: str) -> list[str]:
    paths = re.findall(r"`([^`]+\.ris)`", text)
    return [path.strip() for path in paths]


def resolve_declared_ris(input_dir: Path, package_dir: Path, declared_path: str) -> Path:
    declared = Path(declared_path)
    if declared.is_absolute():
        return declared
    if declared_path.startswith(input_dir.name + "/"):
        return input_dir.parent / declared
    return package_dir / declared


def infer_status(text: str) -> str:
    explicit = first_match(r"Status:\s*(Ready|Caution|Partial|Superseded|Unknown)", text)
    if explicit in STATUS_VALUES:
        return explicit
    lowered = text.lower()
    if any(cue in lowered for cue in PARTIAL_CUES):
        return "Partial"
    if any(cue in lowered for cue in CAUTION_CUES):
        return "Caution"
    if "recommended manuscript text" in lowered and "export file" in lowered:
        return "Ready"
    return "Unknown"


def infer_risk(text: str) -> str:
    lowered = text.lower()
    for cue in HIGH_RISK_CUES:
        if cue in lowered:
            return cue
    return "No major automated cue detected"


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
    match = re.search(heading_pattern, text, flags=re.IGNORECASE)
    if not match:
        return []
    start = match.end()
    next_heading = re.search(r"^##\s+", text[start:], flags=re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end].splitlines()


def extract_claim_rows(package: str, text: str) -> list[dict[str, str]]:
    lines = extract_section_lines(text, r"^##\s+.*Claim[–-]Evidence Matrix.*$")
    rows = split_markdown_table(lines)
    if len(rows) < 2:
        return []
    header = [cell.lower() for cell in rows[0]]
    claim_index = next((i for i, cell in enumerate(header) if "claim" in cell), 0)
    status_index = next((i for i, cell in enumerate(header) if "status" in cell or "strength" in cell), None)
    citation_index = next((i for i, cell in enumerate(header) if "citation" in cell), None)
    output: list[dict[str, str]] = []
    for index, row in enumerate(rows[1:], start=1):
        claim = row[claim_index] if claim_index < len(row) else ""
        if not claim:
            continue
        evidence_status = row[status_index] if status_index is not None and status_index < len(row) else ""
        citations = row[citation_index] if citation_index is not None and citation_index < len(row) else ""
        output.append(
            {
                "claim_id": f"DRAFT-{package}-{index:03d}",
                "package": package,
                "manuscript_section": "",
                "original_claim": claim,
                "recommended_wording": "",
                "evidence_level": "",
                "evidence_type": "",
                "directness": evidence_status,
                "recommended_citations": citations,
                "reviewer_risk": "",
                "action": "verify",
                "notes": "Draft extraction; review manually.",
            }
        )
    return output


def extract_reference_rows(package: str, text: str) -> list[dict[str, str]]:
    lines = extract_section_lines(text, r"^##\s+.*Reference Table.*$")
    rows = split_markdown_table(lines)
    if len(rows) < 2:
        return []
    header = [cell.lower() for cell in rows[0]]
    citation_index = next((i for i, cell in enumerate(header) if "citation" in cell or "short" in cell or "name" in cell), 0)
    key_index = next((i for i, cell in enumerate(header) if "key" in cell or "zotero" in cell), None)
    doi_index = next((i for i, cell in enumerate(header) if "doi" in cell), None)
    pmid_index = next((i for i, cell in enumerate(header) if "pmid" in cell), None)
    output: list[dict[str, str]] = []
    for row in rows[1:]:
        citation = row[citation_index] if citation_index < len(row) else ""
        if not citation:
            continue
        output.append(
            {
                "short_citation": citation,
                "year": "",
                "title": "",
                "canonical_zotero_key": row[key_index] if key_index is not None and key_index < len(row) else "",
                "duplicate_keys": "",
                "doi": row[doi_index] if doi_index is not None and doi_index < len(row) else "",
                "pmid": row[pmid_index] if pmid_index is not None and pmid_index < len(row) else "",
                "pmcid": "",
                "source_used_for_metadata": "unknown",
                "used_in_packages": package,
                "include_in_final_ris": "verify",
                "metadata_warnings": "Draft extraction; review manually.",
            }
        )
    return output


def section_contains(text: str, heading_pattern: str) -> bool:
    return bool(extract_section_lines(text, heading_pattern))


def table_header_has(text: str, heading_pattern: str, required_terms: tuple[str, ...]) -> bool:
    lines = extract_section_lines(text, heading_pattern)
    rows = split_markdown_table(lines)
    if not rows:
        return False
    header = " | ".join(rows[0]).lower()
    return all(term.lower() in header for term in required_terms)


def section_order_ok(text: str, sections: tuple[str, ...]) -> bool:
    position = -1
    for section in sections:
        match = re.search(rf"^##\s+.*{re.escape(section)}.*$", text, flags=re.MULTILINE | re.IGNORECASE)
        if not match or match.start() <= position:
            return False
        position = match.start()
    return True


def detect_ris_markdown_artifacts(ris_text: str) -> list[str]:
    artifacts: list[str] = []
    if re.search(r"^#{1,6}\s", ris_text, flags=re.MULTILINE):
        artifacts.append("Markdown heading")
    if "```" in ris_text:
        artifacts.append("code fence")
    if re.search(r"^[-*]\s+", ris_text, flags=re.MULTILINE):
        artifacts.append("Markdown bullet")
    return artifacts


def detect_unresolved_mismatch(text: str) -> list[str]:
    patterns = (
        r"unresolved metadata mismatch",
        r"possible metadata mismatch",
        r"metadata mismatch remains unresolved",
        r"unresolved duplicate",
    )
    lowered = text.lower()
    return [pattern for pattern in patterns if re.search(pattern, lowered)]


def audit_package(input_dir: Path, folder: Path) -> PackageAudit | None:
    md_path = find_main_markdown(folder)
    if md_path is None:
        return None
    text = read_text(md_path)
    ris_files = sorted(folder.glob("*.ris"))
    ris_file = ris_files[0].name if ris_files else ""
    ris_text = read_text(ris_files[0]) if ris_files else ""
    declared_ris_paths = extract_declared_ris_paths(text)
    declared_existing = [resolve_declared_ris(input_dir, folder, path).exists() for path in declared_ris_paths]
    ris_exists = bool(ris_files) and (all(declared_existing) if declared_existing else True)
    absolute_paths = sorted(set(re.findall(r"/Users/[^`\s)]+", text)))
    return PackageAudit(
        folder=folder.name,
        md_file=md_path.name,
        ris_file=ris_file,
        title=first_match(r"^#\s+(.+)$", text, md_path.stem),
        generated=extract_generated(text),
        status=MANUAL_STATUS_OVERRIDES.get(folder.name, infer_status(text)),
        main_risk=infer_risk(text),
        ris_exists=ris_exists,
        absolute_paths=absolute_paths,
        declared_ris_paths=declared_ris_paths,
        reference_rows=extract_reference_rows(folder.name, text),
        claim_rows=extract_claim_rows(folder.name, text),
        critical_warnings_present=section_contains(text, r"^##\s+.*Critical Warnings.*$"),
        copy_ready_present=section_contains(text, r"^##\s+.*Copy-ready Manuscript Text.*$"),
        claim_matrix_has_evidence_level=table_header_has(text, r"^##\s+.*Claim[–-]Evidence Matrix.*$", ("evidence level",)),
        claim_matrix_has_source_layer=table_header_has(text, r"^##\s+.*Claim[–-]Evidence Matrix.*$", ("source layer",)),
        claim_matrix_has_recommended_action=table_header_has(text, r"^##\s+.*Claim[–-]Evidence Matrix.*$", ("recommended action",)),
        claim_matrix_has_recommended_citation=table_header_has(text, r"^##\s+.*Claim[–-]Evidence Matrix.*$", ("recommended citation",)),
        evidence_logic_chain_present=section_contains(text, r"^##\s+.*Evidence Logic Chain.*$"),
        claims_to_revise_present=section_contains(text, r"^##\s+.*Claims to Revise or Remove.*$"),
        reference_canonicalization_present=section_contains(text, r"^#{2,3}\s+.*Reference Canonicalization Gate.*$"),
        phase10_section_order_ok=section_order_ok(text, PHASE10_SECTIONS),
        ris_markdown_artifacts=detect_ris_markdown_artifacts(ris_text),
        unresolved_mismatch_mentions=detect_unresolved_mismatch(text),
    )


def discover_packages(input_dir: Path) -> list[PackageAudit]:
    packages: list[PackageAudit] = []
    for folder in sorted(path for path in input_dir.iterdir() if path.is_dir()):
        package = audit_package(input_dir, folder)
        if package is not None:
            packages.append(package)
    return packages


def write_summary(input_dir: Path, packages: list[PackageAudit]) -> Path:
    path = input_dir / "PROJECT_SUMMARY.draft.md"
    lines = [
        "# Zotero Evidence Output Project Summary Draft",
        "",
        "This file is generated by `scripts/evidence_output_audit.py` and should be manually reviewed before replacing `PROJECT_SUMMARY.md`.",
        "",
        "## Executive Dashboard",
        "",
        "| Topic | Folder | Status | Main risk | RIS file | RIS exists |",
        "|---|---|---|---|---|---|",
    ]
    for package in packages:
        lines.append(
            f"| {package.title} | `{package.folder}/` | {package.status} | {package.main_risk} | `{package.ris_file}` | {'yes' if package.ris_exists else 'no'} |"
        )
    lines.extend(["", "## QA Warnings", ""])
    warnings = collect_warnings(packages)
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- No automated warnings detected.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_tsv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_claims(input_dir: Path, packages: list[PackageAudit]) -> Path:
    path = input_dir / "evidence_claims_master.draft.tsv"
    fields = [
        "claim_id",
        "package",
        "manuscript_section",
        "original_claim",
        "recommended_wording",
        "evidence_level",
        "evidence_type",
        "directness",
        "recommended_citations",
        "reviewer_risk",
        "action",
        "notes",
    ]
    rows = [row for package in packages for row in package.claim_rows]
    write_tsv(path, rows, fields)
    return path


def write_reference_qc(input_dir: Path, packages: list[PackageAudit]) -> Path:
    path = input_dir / "reference_qc_master.draft.tsv"
    fields = [
        "short_citation",
        "year",
        "title",
        "canonical_zotero_key",
        "duplicate_keys",
        "doi",
        "pmid",
        "pmcid",
        "source_used_for_metadata",
        "used_in_packages",
        "include_in_final_ris",
        "metadata_warnings",
    ]
    rows = [row for package in packages for row in package.reference_rows]
    write_tsv(path, rows, fields)
    return path


def collect_warnings(packages: list[PackageAudit]) -> list[str]:
    warnings: list[str] = []
    for package in packages:
        if package.absolute_paths:
            warnings.append(f"{package.folder}: absolute paths found: {', '.join(package.absolute_paths)}")
        if not package.ris_exists:
            warnings.append(f"{package.folder}: declared or package RIS file is missing")
        if package.status == "Ready" and package.main_risk != "No major automated cue detected":
            warnings.append(f"{package.folder}: status inferred Ready but risk cue found: {package.main_risk}")
        if package.status == "Unknown":
            warnings.append(f"{package.folder}: status could not be inferred")
        if not package.critical_warnings_present:
            warnings.append(f"{package.folder}: missing Critical Warnings section")
        if not package.copy_ready_present:
            warnings.append(f"{package.folder}: missing Copy-ready Manuscript Text section")
        if not package.claim_matrix_has_evidence_level:
            warnings.append(f"{package.folder}: Claim–Evidence Matrix missing Evidence level column")
        if not package.claim_matrix_has_source_layer:
            warnings.append(f"{package.folder}: Claim–Evidence Matrix missing Source layer column")
        if not package.claim_matrix_has_recommended_action:
            warnings.append(f"{package.folder}: Claim–Evidence Matrix missing Recommended action column")
        if not package.claim_matrix_has_recommended_citation:
            warnings.append(f"{package.folder}: Claim–Evidence Matrix missing Recommended citation column")
        if not package.evidence_logic_chain_present:
            warnings.append(f"{package.folder}: missing Evidence Logic Chain section")
        if not package.claims_to_revise_present:
            warnings.append(f"{package.folder}: missing Claims to Revise or Remove section")
        if not package.reference_canonicalization_present:
            warnings.append(f"{package.folder}: missing Reference Canonicalization Gate section")
        if not package.phase10_section_order_ok:
            warnings.append(f"{package.folder}: report sections do not match Phase 10 order")
        if package.ris_markdown_artifacts:
            warnings.append(f"{package.folder}: RIS contains Markdown artifacts: {', '.join(package.ris_markdown_artifacts)}")
        if package.unresolved_mismatch_mentions and package.ris_exists:
            warnings.append(
                f"{package.folder}: metadata mismatch/duplicate cues require checking RIS exclusion: "
                + ", ".join(package.unresolved_mismatch_mentions)
            )
    return warnings


def print_report(packages: list[PackageAudit]) -> None:
    print(f"Scanned packages: {len(packages)}")
    for package in packages:
        ris_state = "ok" if package.ris_exists else "missing"
        print(f"- {package.folder}: {package.status} ({ris_state}) — {package.main_risk}")
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

    wrote: list[Path] = []
    if args.write_summary or not (args.write_summary or args.write_claims or args.write_reference_qc):
        wrote.append(write_summary(input_dir, packages))
    if args.write_claims or not (args.write_summary or args.write_claims or args.write_reference_qc):
        wrote.append(write_claims(input_dir, packages))
    if args.write_reference_qc or not (args.write_summary or args.write_claims or args.write_reference_qc):
        wrote.append(write_reference_qc(input_dir, packages))

    print("\nDraft outputs:")
    for path in wrote:
        print(f"- {path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
