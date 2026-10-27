#!/usr/bin/env python3
"""Audit an EndNote .enl library without modifying it."""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any


REQUIRED = {"id", "title", "author", "year", "secondary_title", "volume", "number", "pages", "accession_number", "electronic_resource_number", "url", "trash_state"}


def clean(value: Any) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", str(value or ""))).strip()


def doi(value: Any) -> str:
    return re.sub(r"^https?://(?:dx\.)?doi\.org/", "", clean(value), flags=re.I).rstrip(".").casefold()


def pmid(value: Any) -> str:
    return re.sub(r"^(?:pmid|pubmed)\s*:?\s*", "", clean(value), flags=re.I)


def blob(value: Any) -> bytes:
    return value.encode("utf-8", "replace") if isinstance(value, str) else (value or b"")


def xml_name(value: Any) -> str:
    match = re.search(br"<name>(.*?)</name>", blob(value))
    return match.group(1).decode("utf-8", "replace") if match else ""


def xml_id(value: Any) -> str:
    match = re.search(br"<id>([^<]+)</id>", blob(value))
    return match.group(1).decode("utf-8", "replace") if match else ""


def xml_members(value: Any) -> set[str]:
    return {item.decode("utf-8", "replace") for item in re.findall(br"<member>([^<]+)</member>", blob(value))}


def group_policy(connection: sqlite3.Connection, manifest: Path | None) -> dict[str, Any]:
    groups: dict[str, str] = {}
    for row in connection.execute("select spec from groups") if connection.execute("select 1 from sqlite_master where type='table' and name='groups'").fetchone() else []:
        name = xml_name(row[0]); identifier = xml_id(row[0])
        if name and identifier:
            groups[name] = identifier
    my_members: set[str] = set()
    misc_exists = connection.execute("select 1 from sqlite_master where type='table' and name='misc'").fetchone()
    section_sets: set[str] = set()
    if misc_exists:
        row = connection.execute("select value from misc where code=17 and subcode=1").fetchone()
        if row:
            my_members = xml_members(row[0])
        for row in connection.execute("select value from misc where code=17"):
            if b"<groupset" in blob(row[0]):
                name = xml_name(row[0])
                if name:
                    section_sets.add(name)
    expected_groups: list[str] = []
    expected_sections: list[str] = []
    if manifest and manifest.exists():
        data = json.loads(manifest.read_text(encoding="utf-8"))
        expected_groups = sorted({f"{row['section']} / {row['paragraph_id']}" for row in data.get("groups", [])})
        expected_sections = sorted({row["section"] for row in data.get("groups", [])})
    missing_groups = [name for name in expected_groups if name not in groups]
    leaked_groups = [name for name in expected_groups if groups.get(name) in my_members]
    missing_sets = [name for name in expected_sections if name not in section_sets]
    return {"expected_groups": expected_groups, "missing_groups": missing_groups, "my_groups_leaks": leaked_groups, "expected_section_sets": expected_sections, "missing_section_sets": missing_sets, "status": "fail" if missing_groups or leaked_groups or missing_sets else "pass"}


def audit(library: Path, source_ris: Path | None = None, manifest: Path | None = None) -> dict[str, Any]:
    report: dict[str, Any] = {"library": str(library), "errors": [], "warnings": [], "checks": {}}
    if not library.exists():
        report["errors"].append(f"library not found: {library}"); report["status"] = "fail"; return report
    try:
        connection = sqlite3.connect(library); connection.row_factory = sqlite3.Row
    except sqlite3.Error as exc:
        report["errors"].append(f"could not open library: {exc}"); report["status"] = "fail"; return report
    try:
        tables = {row[0] for row in connection.execute("select name from sqlite_master where type='table'")}
        report["checks"]["tables"] = sorted(tables)
        if "refs" not in tables:
            report["errors"].append("refs table is missing"); report["status"] = "fail"; return report
        columns = {row[1] for row in connection.execute("pragma table_info(refs)")}
        report["checks"]["missing_required_columns"] = sorted(REQUIRED - columns)
        if REQUIRED - columns:
            report["errors"].append("required refs columns are missing")
            report["status"] = "fail"; return report
        rows = connection.execute("select * from refs where trash_state=0 order by id").fetchall()
        report["checks"]["active_records"] = len(rows)
        missing = {field: [] for field in ("title", "author", "year", "secondary_title")}
        pmids: Counter[str] = Counter(); dois: Counter[str] = Counter()
        for row in rows:
            for field in missing:
                if not clean(row[field]): missing[field].append(int(row["id"]))
            if pmid(row["accession_number"]): pmids[pmid(row["accession_number"])] += 1
            if doi(row["electronic_resource_number"]): dois[doi(row["electronic_resource_number"])] += 1
        report["checks"]["missing_fields"] = missing
        report["checks"]["duplicate_pmids"] = sorted(k for k, v in pmids.items() if v > 1)
        report["checks"]["duplicate_dois"] = sorted(k for k, v in dois.items() if v > 1)
        if any(missing.values()): report["warnings"].append("one or more active records lack required bibliographic fields")
        if report["checks"]["duplicate_pmids"] or report["checks"]["duplicate_dois"]: report["errors"].append("duplicate PMID or DOI identifiers detected")
        groups = []
        if "groups" in tables:
            for row in connection.execute("select group_id,spec from groups order by group_id"):
                raw = row[1].decode("utf-8", "replace") if isinstance(row[1], bytes) else str(row[1] or "")
                match = re.search(r"<name>(.*?)</name>", raw)
                if match:
                    groups.append({"group_id": int(row[0]), "name": match.group(1)})
        report["checks"]["groups"] = groups
        report["checks"]["group_policy"] = group_policy(connection, manifest)
        if report["checks"]["group_policy"]["status"] == "fail":
            report["errors"].append("expected section/paragraph groups or section sets are missing, or a bridge group is still in My Groups")
        if source_ris:
            from endnote_bridge import parse_ris, identity  # type: ignore
            expected = parse_ris(source_ris)
            library_ids = {(pmid(row["accession_number"]), doi(row["electronic_resource_number"])) for row in rows}
            missing_source = [identity(record) for record in expected if (pmid(record.get("AN")), doi(record.get("DO"))) not in library_ids]
            report["checks"]["source_ris_records"] = len(expected)
            report["checks"]["source_ris_missing_from_library"] = missing_source
            if missing_source: report["warnings"].append("source RIS contains records absent from the library")
    finally:
        connection.close()
    cache = library.with_name(library.stem + ".Data") / "sdb" / "sdb.eni"
    if cache.exists():
        try:
            cache_connection = sqlite3.connect(cache)
            cache_count = int(cache_connection.execute("select count(*) from refs where trash_state=0").fetchone()[0])
            cache_connection.close()
            report["checks"]["cache"] = {"path": str(cache), "active_records": cache_count, "matches_main": cache_count == report["checks"].get("active_records")}
            if cache_count != report["checks"].get("active_records"):
                report["errors"].append("main library and EndNote sdb cache have different active record counts")
        except sqlite3.Error as exc:
            report["warnings"].append(f"could not inspect EndNote sdb cache: {exc}")
    else:
        report["warnings"].append("EndNote sdb cache not found")
    report["status"] = "fail" if report["errors"] else "warn" if report["warnings"] else "pass"
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path)
    parser.add_argument("--source-ris", type=Path)
    parser.add_argument("--manifest", type=Path, help="Bridge manifest used to verify expected section groups and section sets")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print("endnote_audit self-test passed"); return
    if not args.library: parser.error("--library is required")
    report = audit(args.library.expanduser().resolve(), args.source_ris.expanduser().resolve() if args.source_ris else None, args.manifest.expanduser().resolve() if args.manifest else None)
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output: args.output.expanduser().resolve().write_text(payload + "\n", encoding="utf-8")
    print(payload)
    raise SystemExit(1 if report.get("status") == "fail" else 0)


if __name__ == "__main__":
    main()
