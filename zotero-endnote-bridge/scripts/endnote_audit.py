#!/usr/bin/env python3
"""Audit an EndNote .enl library without modifying it."""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
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


def audit(library: Path, source_ris: Path | None = None) -> dict[str, Any]:
    report: dict[str, Any] = {"library": str(library), "errors": [], "warnings": [], "checks": {}}
    if not library.exists():
        report["errors"].append(f"library not found: {library}"); return report
    connection = sqlite3.connect(library); connection.row_factory = sqlite3.Row
    try:
        tables = {row[0] for row in connection.execute("select name from sqlite_master where type='table'")}
        report["checks"]["tables"] = sorted(tables)
        if "refs" not in tables:
            report["errors"].append("refs table is missing"); return report
        columns = {row[1] for row in connection.execute("pragma table_info(refs)")}
        report["checks"]["missing_required_columns"] = sorted(REQUIRED - columns)
        if REQUIRED - columns:
            report["errors"].append("required refs columns are missing")
            return report
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
    report["status"] = "fail" if report["errors"] else "warn" if report["warnings"] else "pass"
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path)
    parser.add_argument("--source-ris", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print("endnote_audit self-test passed"); return
    if not args.library: parser.error("--library is required")
    report = audit(args.library.expanduser().resolve(), args.source_ris.expanduser().resolve() if args.source_ris else None)
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output: args.output.expanduser().resolve().write_text(payload + "\n", encoding="utf-8")
    print(payload)
    raise SystemExit(1 if report.get("status") == "fail" else 0)


if __name__ == "__main__":
    main()
