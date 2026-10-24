#!/usr/bin/env python3
"""Build a section/paragraph-aware EndNote handoff package from a canonical RIS.

The script does not search Zotero/PubMed and does not edit an EndNote library.
It consumes a metadata-checked RIS plus explicit manuscript-to-reference
assignments, then writes one master RIS with durable group keywords, selective
per-group RIS files, a JSON manifest, and a human-readable mapping report.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import unicodedata
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "zotero-evidence-output"
TAG_RE = re.compile(r"^([A-Z0-9]{2})  - ?(.*)$")
ZOTERO_KEY_RE = re.compile(r"zotero\s+key\s*:\s*([A-Za-z0-9]+)", re.I)
DOI_RE = re.compile(r"(?:https?://(?:dx\.)?doi\.org/|doi:\s*)?(10\.\d{4,9}/[^\s<>]+)", re.I)
PMID_RE = re.compile(r"^\d+$")

STANDARD_SECTIONS = {"introduction": "Introduction", "methods": "Methods", "results": "Results", "discussion": "Discussion", "conclusion": "Conclusion"}


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a section/paragraph-aware EndNote RIS handoff package")
    parser.add_argument("--ris", help="Canonical, metadata-checked RIS input")
    parser.add_argument("--assignments", help="JSON file containing explicit manuscript section/paragraph assignments")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--slug", help="Output slug; inferred from assignments.run.slug when omitted")
    parser.add_argument("--timestamp", help="YYYY-MM-DD_HHMMSS; current time when omitted")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print planned output paths without writing")
    parser.add_argument("--self-test", action="store_true", help="Run a temporary fixture-based self-test")
    return parser.parse_args()


def text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, (list, tuple)):
        return "; ".join(text(item) for item in value if text(item))
    return str(value)


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).lower()


def normalize_doi(value: str) -> str:
    match = DOI_RE.search(value.strip())
    if not match:
        return ""
    return match.group(1).rstrip(".,;)").lower()


def normalize_pmid(value: str) -> str:
    value = value.strip()
    return value if PMID_RE.fullmatch(value) else ""


def normalize_title(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).lower()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def safe_slug(value: str, default: str = "unassigned") -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-._")
    return value[:80] or default


def canonical_section(value: str) -> str:
    cleaned = text(value, "Unassigned").strip()
    return STANDARD_SECTIONS.get(cleaned.lower(), cleaned or "Unassigned")


def parse_ris(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        fail(f"RIS input does not exist: {path}")
    records: list[dict[str, Any]] = []
    current: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip("\r")
        if line.startswith("TY  - ") and current:
            records.append(build_record(current))
            current = []
        if line.strip():
            current.append(line)
        if line.startswith("ER  -"):
            records.append(build_record(current))
            current = []
    if current:
        records.append(build_record(current))
    records = [record for record in records if record.get("tags")]
    if not records:
        fail("RIS input contains no records")
    return records


def build_record(lines: list[str]) -> dict[str, Any]:
    tags: dict[str, list[str]] = defaultdict(list)
    for line in lines:
        match = TAG_RE.match(line)
        if match:
            tags[match.group(1)].append(match.group(2).strip())
    first = lambda key: tags.get(key, [""])[0]
    return {
        "lines": list(lines),
        "tags": tags,
        "doi": normalize_doi(first("DO")),
        "pmid": normalize_pmid(first("AN")),
        "zotero_key": next((m.group(1) for value in tags.get("N1", []) if (m := ZOTERO_KEY_RE.search(value))), ""),
        "title": first("TI"),
        "author": first("AU"),
        "year": first("PY") or first("Y1"),
    }


def load_assignments(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"assignment input does not exist: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"assignment input is not valid JSON: {exc}")
    if not isinstance(payload, dict):
        fail("assignment root must be an object")
    assignments = payload.get("assignments")
    if not isinstance(assignments, list) or not assignments:
        fail("assignment input requires a non-empty assignments list")
    for index, item in enumerate(assignments, start=1):
        if not isinstance(item, dict):
            fail(f"assignments[{index}] must be an object")
        if not text(item.get("section")):
            fail(f"assignments[{index}].section is required")
        refs = item.get("references")
        if not isinstance(refs, list) or not refs:
            fail(f"assignments[{index}].references must be a non-empty list")
        for ref_index, ref in enumerate(refs, start=1):
            if not isinstance(ref, dict):
                fail(f"assignments[{index}].references[{ref_index}] must be an object")
            if not any(text(ref.get(key)) for key in ("doi", "pmid", "zotero_key", "title")):
                fail(f"assignments[{index}].references[{ref_index}] needs doi, pmid, zotero_key, or title")
    return payload


def index_records(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    index: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        for key in (record["doi"], record["pmid"], record["zotero_key"], normalize_title(record["title"])):
            if key:
                index[key].append(record)
    return index


def resolve_reference(ref: dict[str, Any], index: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    keys = [normalize_doi(text(ref.get("doi"))), normalize_pmid(text(ref.get("pmid"))), text(ref.get("zotero_key")).strip(), normalize_title(text(ref.get("title")))]
    for key in keys:
        if not key:
            continue
        matches = index.get(key, [])
        unique = {id(record): record for record in matches}
        if len(unique) == 1:
            return next(iter(unique.values()))
        if len(unique) > 1:
            fail(f"ambiguous reference identifier {key!r}; use DOI/PMID or a canonical Zotero key")
    fail("assignment reference did not match any RIS record: " + json.dumps(ref, ensure_ascii=False))


def ris_lines(record: dict[str, Any], groups: list[dict[str, Any]]) -> list[str]:
    lines = [line for line in record["lines"] if not line.startswith("ER  -")]
    keywords: list[str] = []
    notes: list[str] = []
    for group in groups:
        keywords.extend([
            f"Manuscript section: {group['section']}",
            f"Manuscript paragraph: {group['paragraph_id']}",
            f"Manuscript group: {group['group_path']}",
        ])
        if group["claim_ids"]:
            keywords.extend(f"Claim: {claim}" for claim in group["claim_ids"])
        if group["roles"]:
            keywords.extend(f"Evidence role: {role}" for role in group["roles"])
        notes.append(f"Manuscript group: {group['group_path']}")
    existing_keywords = {normalize(value) for value in record["tags"].get("KW", [])}
    for keyword in dict.fromkeys(keywords):
        if normalize(keyword) not in existing_keywords:
            lines.append(f"KW  - {keyword}")
    existing_notes = {normalize(value) for value in record["tags"].get("N1", [])}
    for note in dict.fromkeys(notes):
        if normalize(note) not in existing_notes:
            lines.append(f"N1  - {note}")
    lines.append("ER  -")
    return lines


def record_text(record: dict[str, Any], groups: list[dict[str, Any]]) -> str:
    return "\n".join(ris_lines(record, groups)) + "\n\n"


def output_dir(root: Path, slug: str, timestamp: str) -> Path:
    stem = f"{slug}_{timestamp}"
    directory = root / stem
    version = 2
    while directory.exists():
        directory = root / f"{stem}_v{version}"
        version += 1
    return directory


def build_package(ris_path: Path, assignment_path: Path, root: Path, slug: str | None, timestamp: str | None, dry_run: bool = False) -> dict[str, Any]:
    records = parse_ris(ris_path)
    payload = load_assignments(assignment_path)
    run = payload.get("run") if isinstance(payload.get("run"), dict) else {}
    slug = safe_slug(slug or text(run.get("slug")) or ris_path.stem.replace("_references", ""), "manuscript")
    timestamp = timestamp or datetime.now().strftime("%Y-%m-%d_%H%M%S")
    try:
        datetime.strptime(timestamp, "%Y-%m-%d_%H%M%S")
    except ValueError:
        fail("timestamp must use YYYY-MM-DD_HHMMSS")
    run_dir = output_dir(root, slug, timestamp)

    index = index_records(records)
    groups_by_record: dict[int, list[dict[str, Any]]] = defaultdict(list)
    group_records: dict[str, list[dict[str, Any]]] = defaultdict(list)
    assignment_rows: list[dict[str, Any]] = []
    for item in payload["assignments"]:
        section = canonical_section(text(item.get("section")))
        paragraph_id = text(item.get("paragraph_id"))
        if not paragraph_id:
            number = item.get("paragraph")
            paragraph_id = f"{section}-{int(number):02d}" if str(number).isdigit() else f"{section}-Unassigned"
        paragraph_id = paragraph_id.strip()
        group_path = f"{section}/{paragraph_id}"
        claim_ids = [text(value).strip() for value in item.get("claim_ids", []) if text(value).strip()]
        for ref in item["references"]:
            record = resolve_reference(ref, index)
            role = text(ref.get("role"), "support").strip() or "support"
            group = {
                "section": section,
                "paragraph_id": paragraph_id,
                "group_path": group_path,
                "claim_ids": claim_ids,
                "roles": [role],
                "role": role,
            }
            groups_by_record[id(record)].append(group)
            if record not in group_records[group_path]:
                group_records[group_path].append(record)
            assignment_rows.append({
                "group_path": group_path,
                "section": section,
                "paragraph_id": paragraph_id,
                "claim_ids": claim_ids,
                "role": role,
                "doi": record["doi"],
                "pmid": record["pmid"],
                "zotero_key": record["zotero_key"],
                "title": record["title"],
                "author": record["author"],
                "year": record["year"],
            })

    for record in records:
        if id(record) not in groups_by_record:
            group = {"section": "Unassigned", "paragraph_id": "Unassigned", "group_path": "Unassigned/Unassigned", "claim_ids": [], "roles": ["unassigned"], "role": "unassigned"}
            groups_by_record[id(record)].append(group)
            if record not in group_records[group["group_path"]]:
                group_records[group["group_path"]].append(record)
            assignment_rows.append({"group_path": group["group_path"], "section": "Unassigned", "paragraph_id": "Unassigned", "claim_ids": [], "role": "unassigned", "doi": record["doi"], "pmid": record["pmid"], "zotero_key": record["zotero_key"], "title": record["title"], "author": record["author"], "year": record["year"]})

    master = run_dir / f"{run_dir.name}_all_references.ris"
    manifest = run_dir / f"{run_dir.name}_collection_manifest.json"
    report = run_dir / f"{run_dir.name}_manuscript_reference_map.md"
    endnote_dir = run_dir / "endnote-import"
    planned = {"run_dir": run_dir, "master_ris": master, "manifest": manifest, "report": report, "endnote_dir": endnote_dir}
    if dry_run:
        return {key: str(value) for key, value in planned.items()}

    endnote_dir.mkdir(parents=True, exist_ok=False)
    master.write_text("".join(record_text(record, groups_by_record[id(record)]) for record in records), encoding="utf-8")
    for group_path, group_records_list in sorted(group_records.items()):
        section, paragraph = group_path.split("/", 1)
        directory = endnote_dir / safe_slug(section, "section")
        directory.mkdir(parents=True, exist_ok=True)
        group_file = directory / f"{safe_slug(paragraph, 'paragraph')}.ris"
        group_file.write_text("".join(record_text(record, groups_by_record[id(record)]) for record in group_records_list), encoding="utf-8")

    groups = []
    for group_path, group_records_list in sorted(group_records.items()):
        groups.append({"group_path": group_path, "record_count": len(group_records_list), "identifiers": [{"doi": record["doi"], "pmid": record["pmid"], "zotero_key": record["zotero_key"], "title": record["title"]} for record in group_records_list]})
    manifest.write_text(json.dumps({"run": run, "source_ris": str(ris_path.name), "master_ris": master.name, "import_once_rule": "Import the master RIS once; per-group RIS files are selective handoffs and may duplicate records.", "groups": groups, "assignments": assignment_rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    rows = ["# Manuscript Reference Map", "", "Import rule: import the master RIS once. The per-group RIS files are selective handoffs; importing several of them can create duplicates.", "", "| Group | Role | Claim IDs | Author | Year | Title | DOI | PMID | Zotero key |", "|---|---|---|---|---:|---|---|---|---|"]
    for row in sorted(assignment_rows, key=lambda item: (item["group_path"], item["title"], item["role"])):
        cells = [row["group_path"], row["role"], "; ".join(row["claim_ids"]) or "—", row["author"], row["year"], row["title"], row["doi"] or "—", row["pmid"] or "—", row["zotero_key"] or "—"]
        rows.append("| " + " | ".join(value.replace("|", "\\|").replace("\n", " ") for value in cells) + " |")
    rows.extend(["", "## EndNote group plan", "", "- Create top-level groups: `Introduction`, `Methods`, `Results`, `Discussion`, and any other section present.", "- Create child groups from `group_path`, such as `Discussion/Discussion-01`.", "- The master RIS carries the same hierarchy as `KW` fields (`Manuscript section`, `Manuscript paragraph`, and `Manuscript group`).", "- If EndNote Smart Groups are available, filter on `Manuscript group: <section>/<paragraph_id>`; otherwise use the manifest for one-time custom-group assignment."])
    report.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return {key: str(value) for key, value in planned.items()}


def self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        ris = root / "source.ris"
        ris.write_text("""TY  - JOUR\nAU  - Example, A.\nPY  - 2024\nTI  - First paper\nDO  - 10.1000/first\nAN  - 12345678\nER  -\n\nTY  - JOUR\nAU  - Other, B.\nPY  - 2023\nTI  - Second paper\nDO  - 10.1000/second\nAN  - 23456789\nER  -\n""", encoding="utf-8")
        assignments = root / "assignments.json"
        assignments.write_text(json.dumps({"run": {"slug": "demo"}, "assignments": [{"section": "Discussion", "paragraph": 1, "claim_ids": ["C01"], "references": [{"doi": "10.1000/first", "role": "direct_support"}]}, {"section": "Methods", "paragraph_id": "Methods-02", "references": [{"pmid": "23456789", "role": "method"}]}]}), encoding="utf-8")
        result = build_package(ris, assignments, root / "out", None, "2026-01-01_010203")
        master = Path(result["master_ris"])
        assert master.exists() and "Manuscript group: Discussion/Discussion-01" in master.read_text(encoding="utf-8")
        assert (Path(result["endnote_dir"]) / "Discussion" / "Discussion-01.ris").exists()
        assert (Path(result["endnote_dir"]) / "Methods" / "Methods-02.ris").exists()
    print("Self-test passed.")


def main() -> None:
    args = parse_args()
    if args.self_test:
        self_test()
        return
    if not args.ris or not args.assignments:
        fail("--ris and --assignments are required unless --self-test is used")
    result = build_package(Path(args.ris), Path(args.assignments), Path(args.output_root), args.slug, args.timestamp, args.dry_run)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
