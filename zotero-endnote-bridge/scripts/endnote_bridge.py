#!/usr/bin/env python3
"""Build and optionally apply a Zotero-to-EndNote handoff package.

The package path is pure Python and safe to run anywhere.  The optional
SQLite adapter is intentionally explicit because EndNote's library schema is
private and release dependent.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import sqlite3
import struct
import subprocess
import sys
import time
import unicodedata
import uuid
from pathlib import Path
from typing import Any, Iterable
from xml.sax.saxutils import escape


PRIORITY_RANK = {"P1": 1, "P2": 2, "P3": 3}
REQUIRED_TABLES = {"refs", "groups", "misc"}
REQUIRED_REF_COLUMNS = {"id", "title", "author", "year", "secondary_title", "volume", "number", "pages", "url", "accession_number", "electronic_resource_number", "keywords", "research_notes", "trash_state"}


def text(value: Any) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", str(value or ""))).strip()


def norm(value: Any) -> str:
    return text(value).casefold()


def clean_doi(value: Any) -> str:
    return re.sub(r"^https?://(?:dx\.)?doi\.org/", "", text(value), flags=re.I).rstrip(".").casefold()


def clean_pmid(value: Any) -> str:
    return re.sub(r"^(?:pmid|pubmed)\s*:?\s*", "", text(value), flags=re.I)


def year_of(record: dict[str, Any]) -> str:
    value = text(record.get("PY") or record.get("Y1") or record.get("DA"))
    match = re.search(r"(?:19|20)\d{2}", value)
    return match.group(0) if match else ""


def title_of(record: dict[str, Any]) -> str:
    return text(record.get("TI") or record.get("T1")).rstrip(".")


def authors_of(record: dict[str, Any]) -> list[str]:
    value = record.get("AU") or []
    if isinstance(value, str):
        return [x for x in value.split("\n") if text(x)]
    return [text(x) for x in value if text(x)]


def first_author(record: dict[str, Any]) -> str:
    return authors_of(record)[0].split(",", 1)[0].strip() if authors_of(record) else ""


def identity(record: dict[str, Any]) -> tuple[str, str, tuple[str, str, str]]:
    return clean_pmid(record.get("AN")), clean_doi(record.get("DO")), (norm(title_of(record)), norm(first_author(record)), year_of(record))


def parse_ris(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    current: dict[str, Any] = {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.rstrip("\r\n")
        if line.strip() == "ER  -":
            if current:
                records.append(current)
            current = {}
            continue
        match = re.match(r"^([A-Z0-9]{2})\s+-\s?(.*)$", line)
        if not match:
            continue
        tag, value = match.groups()
        if tag in {"AU", "KW"}:
            current.setdefault(tag, []).append(value)
        elif tag in current:
            current[tag] = f"{current[tag]}\n{value}"
        else:
            current[tag] = value
    if current:
        records.append(current)
    return records


def ris_value(record: dict[str, Any], tag: str) -> str:
    value = record.get(tag, "")
    return "\n".join(value) if isinstance(value, list) else text(value)


def ris_line(tag: str, value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [f"{tag}  - {text(v)}" for v in value if text(v)]
    return [f"{tag}  - {text(value)}"]


def render_ris(record: dict[str, Any]) -> str:
    lines = ["TY  - JOUR"]
    lines += ris_line("TI", title_of(record))
    lines += ris_line("AU", authors_of(record))
    lines += ris_line("PY", year_of(record))
    lines += ris_line("JO", record.get("JO") or record.get("J2"))
    lines += ris_line("VL", record.get("VL"))
    lines += ris_line("IS", record.get("IS"))
    pages = text(record.get("SP"))
    if record.get("EP"):
        pages = f"{pages}-{text(record.get('EP'))}" if pages else text(record.get("EP"))
    lines += ris_line("SP", pages)
    lines += ris_line("DO", clean_doi(record.get("DO")))
    lines += ris_line("AN", clean_pmid(record.get("AN")))
    lines += ris_line("UR", record.get("UR"))
    lines += ris_line("KW", record.get("KW") or [])
    lines += ris_line("N1", record.get("N1"))
    lines.append("ER  -")
    return "\n".join(lines) + "\n"


def canonical_records(paths: Iterable[Path]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    seen_pmid: dict[str, int] = {}
    seen_doi: dict[str, int] = {}
    seen_fallback: dict[tuple[str, str, str], int] = {}
    duplicates: list[dict[str, Any]] = []
    for path in paths:
        for record in parse_ris(path):
            key = identity(record)
            if not key[0] and not key[1] and not key[2][0]:
                raise ValueError(f"record without title/identifier in {path}")
            idx = seen_pmid.get(key[0]) if key[0] else None
            if idx is None and key[1]:
                idx = seen_doi.get(key[1])
            # Title/author/year is only a fallback when at least one side has
            # no canonical identifier. Two differently identified papers can
            # legitimately share a title (for example the same nomenclature
            # consensus published in two journals).
            if idx is None and not key[0] and not key[1]:
                idx = seen_fallback.get(key[2])
            if idx is None:
                idx = len(records)
                record = dict(record)
                record["_source_ris"] = str(path)
                records.append(record)
                if key[0]: seen_pmid[key[0]] = idx
                if key[1]: seen_doi[key[1]] = idx
                seen_fallback[key[2]] = idx
            else:
                duplicates.append({"source": str(path), "title": title_of(record), "canonical_index": idx})
                existing = records[idx]
                old_pmid, old_doi, _ = identity(existing)
                if key[0] and old_pmid and key[0] != old_pmid:
                    raise ValueError(f"conflicting PMID values for DOI/title: {old_pmid} vs {key[0]}")
                if key[1] and old_doi and key[1] != old_doi:
                    raise ValueError(f"conflicting DOI values for PMID/title: {old_doi} vs {key[1]}")
                for tag in ("AU", "KW"):
                    vals = existing.setdefault(tag, [])
                    for item in record.get(tag, []) or []:
                        if item not in vals:
                            vals.append(item)
                for tag in ("AN", "DO", "UR", "JO", "VL", "IS", "SP", "EP", "PY", "N1"):
                    if not existing.get(tag) and record.get(tag):
                        existing[tag] = record[tag]
                if key[0]: seen_pmid[key[0]] = idx
                if key[1]: seen_doi[key[1]] = idx
    return records, duplicates


def load_assignments(path: Path | None) -> list[dict[str, Any]]:
    if path is None:
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    assignments = data.get("assignments", data) if isinstance(data, dict) else data
    if not isinstance(assignments, list):
        raise ValueError("assignments JSON must contain a list under 'assignments'")
    out: list[dict[str, Any]] = []
    for row in assignments:
        if not isinstance(row, dict):
            raise ValueError("each assignment must be an object")
        section = text(row.get("section")) or "Unassigned"
        paragraph_id = text(row.get("paragraph_id")) or "Unassigned"
        refs = row.get("references", [])
        if not isinstance(refs, list):
            raise ValueError(f"references must be a list for {paragraph_id}")
        out.append({**row, "section": section, "paragraph_id": paragraph_id, "references": refs})
    return out


def reference_matches(record: dict[str, Any], ref: dict[str, Any]) -> bool:
    if ref.get("doi") and clean_doi(ref["doi"]) == clean_doi(record.get("DO")):
        return True
    if ref.get("pmid") and clean_pmid(ref["pmid"]) == clean_pmid(record.get("AN")):
        return True
    if ref.get("zotero_key") and text(ref["zotero_key"]) == text(record.get("ZK")):
        return True
    if ref.get("title") and norm(ref["title"]) == norm(title_of(record)):
        return True
    return False


def enrich_assignments(records: list[dict[str, Any]], assignments: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_idx: dict[int, list[dict[str, Any]]] = {i: [] for i in range(len(records))}
    warnings: list[dict[str, Any]] = []
    for row in assignments:
        section, paragraph = row["section"], row["paragraph_id"]
        for ref in row["references"]:
            matches = [i for i, r in enumerate(records) if reference_matches(r, ref)]
            if len(matches) != 1:
                warnings.append({"type": "unresolved_assignment" if not matches else "ambiguous_assignment", "section": section, "paragraph_id": paragraph, "reference": ref, "matches": matches})
                continue
            idx = matches[0]
            entry = {"section": section, "paragraph_id": paragraph, "paragraph_title": text(row.get("paragraph_title")), "priority": text(ref.get("priority")) or "P2", "role": text(ref.get("role")) or "evidence", "claim_ids": ref.get("claim_ids", []), "note": text(ref.get("note"))}
            by_idx[idx].append(entry)
    for idx, record in enumerate(records):
        memberships = by_idx[idx]
        if not memberships:
            memberships = [{"section": "Unassigned", "paragraph_id": "Unassigned", "paragraph_title": "", "priority": "P3", "role": "unassigned", "claim_ids": [], "note": ""}]
            warnings.append({"type": "unassigned_record", "title": title_of(record), "index": idx})
        record["_assignments"] = memberships
        keywords = list(record.get("KW") or [])
        notes = [text(record.get("N1"))] if record.get("N1") else []
        for item in memberships:
            path = f"{item['section']}/{item['paragraph_id']}"
            keywords.extend([f"Manuscript section: {item['section']}", f"Manuscript paragraph: {item['paragraph_id']}", f"Manuscript group: {path}", f"Priority: {item['priority']}", f"Evidence role: {item['role']}"])
            if item["claim_ids"]:
                keywords.append("Claim IDs: " + ", ".join(map(str, item["claim_ids"])))
            notes.append(f"Bridge assignment: {path}; priority={item['priority']}; role={item['role']}.")
        record["KW"] = list(dict.fromkeys(keywords))
        record["N1"] = "\r".join(dict.fromkeys(x for x in notes if x))
    return records, warnings


def group_key(item: dict[str, Any]) -> tuple[str, str]:
    return item["section"], item["paragraph_id"]


def write_package(records: list[dict[str, Any]], duplicates: list[dict[str, Any]], warnings: list[dict[str, Any]], output: Path, source_paths: list[Path], assignments_path: Path | None) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    (output / "groups").mkdir(exist_ok=True)
    (output / "master.ris").write_text("".join(render_ris(r) for r in records), encoding="utf-8")
    groups: dict[tuple[str, str], list[int]] = {}
    for idx, record in enumerate(records):
        for item in record["_assignments"]:
            groups.setdefault(group_key(item), []).append(idx)
    group_rows: list[dict[str, Any]] = []
    for (section, paragraph), indices in sorted(groups.items()):
        safe = re.sub(r"[^A-Za-z0-9._-]+", "_", f"{section}__{paragraph}").strip("_") or "Unassigned"
        path = output / "groups" / f"{safe}.ris"
        unique_indices = list(dict.fromkeys(indices))
        path.write_text("".join(render_ris(records[i]) for i in sorted(unique_indices, key=lambda i: (min(PRIORITY_RANK.get(x["priority"], 9) for x in records[i]["_assignments"] if x["section"] == section and x["paragraph_id"] == paragraph), title_of(records[i])))), encoding="utf-8")
        group_rows.append({"section": section, "paragraph_id": paragraph, "path": str(path.relative_to(output)), "members": len(unique_indices), "record_indices": unique_indices})
    manifest = {
        "schema_version": "1.0",
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "sources": [{"path": str(p), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in source_paths],
        "assignments": str(assignments_path) if assignments_path else None,
        "records": [{"index": i, "title": title_of(r), "doi": clean_doi(r.get("DO")), "pmid": clean_pmid(r.get("AN")), "assignments": r["_assignments"]} for i, r in enumerate(records)],
        "groups": group_rows,
        "duplicates_collapsed": duplicates,
        "warnings": warnings,
        "write_policy": "package-only unless --apply --apply-sqlite is explicitly requested",
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    with (output / "group-map.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["section", "paragraph_id", "path", "members"])
        writer.writeheader()
        writer.writerows([{k: row[k] for k in ("section", "paragraph_id", "path", "members")} for row in group_rows])
    return manifest


def endnote_running() -> bool:
    try:
        result = subprocess.run(["pgrep", "-alf", "EndNote"], capture_output=True, text=True, check=False)
    except FileNotFoundError:
        return False
    return any("EndNote" in line and "pgrep" not in line for line in result.stdout.splitlines())


def backup_library(library: Path) -> Path:
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    destination = library.parent / f"{library.stem}.backup_before_zotero_bridge_{stamp}"
    suffix = 1
    while destination.exists():
        destination = library.parent / f"{library.stem}.backup_before_zotero_bridge_{stamp}_{suffix}"
        suffix += 1
    destination.mkdir()
    shutil.copy2(library, destination / library.name)
    data = library.with_name(library.stem + ".Data")
    if data.exists():
        shutil.copytree(data, destination / data.name)
    return destination


def member_blob(ids: list[int]) -> bytes:
    return struct.pack(">I", 2) + struct.pack("<I", len(ids)) + b"".join(struct.pack("<I", i) for i in ids)


def xml_name(blob: bytes | str) -> str:
    raw = blob.encode("utf-8", "replace") if isinstance(blob, str) else (blob or b"")
    match = re.search(br"<name>(.*?)</name>", raw)
    return match.group(1).decode("utf-8", "replace") if match else ""


def group_spec(name: str, now: int) -> tuple[bytes, str]:
    gid = str(uuid.uuid4()).upper()
    xml = f'<?xml version="1.0" encoding="UTF-8"?><group version="1"><ids><id>{gid}</id><name>{escape(name)}</name></ids><times><created format="UTC">{now}</created><modified format="UTC">{now}</modified></times><rules><rule>TYPE;3</rule></rules></group>'
    return xml.encode(), gid


def groupset_xml(name: str, child_ids: list[str], now: int) -> tuple[bytes, str]:
    gid = str(uuid.uuid4()).upper()
    members = "".join(f"<member>{x}</member>" for x in child_ids)
    xml = f'<?xml version="1.0" encoding="UTF-8"?><groupset version="1"><ids><id>{gid}</id><name>{escape(name)}</name></ids><times><created format="UTC">{now}</created><modified format="UTC">{now}</modified></times><members complex="true">{members}</members></groupset>'
    return xml.encode(), gid


def schema_check(connection: sqlite3.Connection) -> None:
    tables = {row[0] for row in connection.execute("select name from sqlite_master where type='table'")}
    missing = REQUIRED_TABLES - tables
    if missing:
        raise RuntimeError(f"unsupported EndNote schema; missing tables: {sorted(missing)}")
    cols = {row[1] for row in connection.execute("pragma table_info(refs)")}
    if not REQUIRED_REF_COLUMNS <= cols:
        raise RuntimeError(f"unsupported EndNote schema; missing refs columns: {sorted(REQUIRED_REF_COLUMNS - cols)}")


def field_value(record: dict[str, Any], name: str) -> str:
    mapping = {"title": title_of(record), "author": "\r".join(authors_of(record)), "year": year_of(record), "secondary_title": text(record.get("JO") or record.get("J2")), "volume": text(record.get("VL")), "number": text(record.get("IS")), "pages": text(record.get("SP")) + (f"-{text(record.get('EP'))}" if record.get("EP") else ""), "url": text(record.get("UR")), "accession_number": clean_pmid(record.get("AN")), "electronic_resource_number": clean_doi(record.get("DO")), "keywords": "\r".join(record.get("KW") or []), "research_notes": text(record.get("N1"))}
    return mapping.get(name, "")


def append_lines(old: Any, new: str) -> str:
    values = [x for x in str(old or "").split("\r") if x]
    for value in str(new or "").split("\r"):
        if value and value not in values:
            values.append(value)
    return "\r".join(values)


def sync_cache(library: Path) -> Path | None:
    cache_path = library.with_name(library.stem + ".Data") / "sdb" / "sdb.eni"
    if not cache_path.exists():
        return None
    main = sqlite3.connect(library)
    cache = sqlite3.connect(cache_path)
    try:
        cache.execute("begin immediate")
        for table in ("refs", "refs_ord", "ref_props", "ret_watch", "file_res", "csort", "terms", "jterms", "groups", "tag_groups", "misc"):
            if cache.execute("select 1 from sqlite_master where type='table' and name=?", (table,)).fetchone():
                cache.execute(f'delete from "{table}"')
        for table in ("refs", "refs_ord", "ref_props", "ret_watch", "file_res", "csort", "terms", "jterms", "groups", "tag_groups", "misc"):
            if not main.execute("select 1 from sqlite_master where type='table' and name=?", (table,)).fetchone() or not cache.execute("select 1 from sqlite_master where type='table' and name=?", (table,)).fetchone():
                continue
            main_cols = {row[1] for row in main.execute(f'pragma table_info("{table}")')}
            cache_cols = {row[1] for row in cache.execute(f'pragma table_info("{table}")')}
            cols = sorted(main_cols & cache_cols)
            if not cols:
                continue
            rows = main.execute(f'select {",".join(cols)} from "{table}"').fetchall()
            if rows:
                placeholders = ",".join("?" for _ in cols)
                cache.executemany(f'insert into "{table}" ({",".join(cols)}) values ({placeholders})', rows)
        cache.commit()
    except Exception:
        cache.rollback()
        raise
    finally:
        main.close(); cache.close()
    return cache_path


def apply_sqlite(library: Path, records: list[dict[str, Any]], output: Path) -> dict[str, Any]:
    if endnote_running():
        raise RuntimeError("EndNote is running; close it before --apply-sqlite")
    if not library.exists():
        raise FileNotFoundError(library)
    backup = backup_library(library)
    connection = sqlite3.connect(library)
    connection.row_factory = sqlite3.Row
    schema_check(connection)
    existing = connection.execute("select * from refs where trash_state=0 order by id").fetchall()
    by_pmid: dict[str, list[sqlite3.Row]] = {}; by_doi: dict[str, list[sqlite3.Row]] = {}; by_fallback: dict[tuple[str, str, str], list[sqlite3.Row]] = {}
    for row in existing:
        if clean_pmid(row["accession_number"]): by_pmid.setdefault(clean_pmid(row["accession_number"]), []).append(row)
        if clean_doi(row["electronic_resource_number"]): by_doi.setdefault(clean_doi(row["electronic_resource_number"]), []).append(row)
        first = str(row["author"] or "").split("\r", 1)[0].split(",", 1)[0]
        by_fallback.setdefault((norm(row["title"]), norm(first), text(row["year"])), []).append(row)
    record_ids: dict[int, int] = {}
    new_records = 0; updated_records = 0; matched_records = 0
    now = int(time.time())
    try:
        with connection:
            cols = [row[1] for row in connection.execute("pragma table_info(refs)") if row[1] != "id"]
            for idx, record in enumerate(records):
                pmid, doi, fallback = identity(record)
                matches = by_pmid.get(pmid, []) if pmid else []
                if not matches and doi:
                    matches = by_doi.get(doi, [])
                if not matches:
                    candidates = by_fallback.get(fallback, [])
                    matches = candidates if not (pmid or doi) else [row for row in candidates if not clean_pmid(row["accession_number"]) and not clean_doi(row["electronic_resource_number"])]
                if len(matches) > 1:
                    raise RuntimeError(f"ambiguous existing identity for {title_of(record)!r}: {[int(r['id']) for r in matches]}")
                if matches:
                    rid = int(matches[0]["id"]); matched_records += 1
                    row = matches[0]
                    keywords = append_lines(row["keywords"], "\r".join(record.get("KW") or []))
                    notes = append_lines(row["research_notes"], record.get("N1", ""))
                    assignments = ["keywords=?", "research_notes=?"]; params: list[Any] = [keywords, notes]
                    for field in ("secondary_title", "volume", "number", "pages", "url"):
                        value = field_value(record, field)
                        if value and not text(row[field]):
                            assignments.append(f"{field}=?"); params.append(value)
                    if keywords != text(row["keywords"]) or notes != text(row["research_notes"]) or len(assignments) > 2:
                        assignments.append("record_last_updated=?"); params.extend([now, rid]); connection.execute(f"update refs set {','.join(assignments)} where id=?", params); updated_records += 1
                else:
                    values = {column: "" for column in cols}; values.update({"trash_state": 0, "reference_type": 0, "added_to_library": now, "record_last_updated": now})
                    for field in values:
                        if field in REQUIRED_REF_COLUMNS:
                            values[field] = field_value(record, field)
                    query_cols = ",".join(cols)
                    connection.execute(f"insert into refs ({query_cols}) values ({','.join('?' for _ in cols)})", [values.get(column, "") for column in cols])
                    rid = int(connection.execute("select last_insert_rowid()").fetchone()[0]); new_records += 1
                record_ids[idx] = rid
            # Build/update paragraph groups without touching unrelated groups.
            group_members: dict[tuple[str, str], list[int]] = {}
            for idx, record in enumerate(records):
                for item in record["_assignments"]:
                    group_members.setdefault(group_key(item), []).append(record_ids[idx])
            existing_groups = {xml_name(row["spec"]): int(row["group_id"]) for row in connection.execute("select group_id,spec from groups")}
            group_ids: dict[tuple[str, str], str] = {}
            for key, members in sorted(group_members.items()):
                name = f"{key[0]} / {key[1]}"; member_ids = sorted(set(members))
                if name in existing_groups:
                    gid_row = connection.execute("select spec from groups where group_id=?", (existing_groups[name],)).fetchone()
                    raw_spec = gid_row[0] if gid_row else b""
                    raw_spec = raw_spec.encode("utf-8", "replace") if isinstance(raw_spec, str) else raw_spec
                    match = re.search(br"<id>([^<]+)</id>", raw_spec)
                    gid = match.group(1).decode() if match else str(uuid.uuid4()).upper()
                    connection.execute("update groups set members=? where group_id=?", (member_blob(member_ids), existing_groups[name]))
                else:
                    spec, gid = group_spec(name, now); next_id = int(connection.execute("select coalesce(max(group_id),0)+1 from groups").fetchone()[0]); connection.execute("insert into groups(group_id,recs_stamp,spec,members) values(?,?,?,?)", (next_id, 0, spec, member_blob(member_ids)))
                group_ids[key] = gid
            # Store section sets in EndNote's misc group-set records when the
            # current schema exposes them. The paragraph groups remain usable
            # even if a future EndNote release omits this private table shape.
            for section in sorted({key[0] for key in group_members}):
                children = [group_ids[key] for key in sorted(group_ids) if key[0] == section]
                xml, _ = groupset_xml(section, children, now)
                connection.execute("insert or replace into misc(code,subcode,value) values(17,?,?)", (100 + sorted({key[0] for key in group_members}).index(section), xml))
        connection.close()
        cache = sync_cache(library)
    except Exception:
        connection.close()
        raise
    report = {"library": str(library), "backup": str(backup), "new_records": new_records, "matched_records": matched_records, "updated_records": updated_records, "cache_synchronized": str(cache) if cache else None, "groups": len(group_members)}
    (output / "apply-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def self_test() -> None:
    import tempfile
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory); ris = root / "sample.ris"; assignments = root / "assignments.json"; output = root / "out"
        ris.write_text("TY  - JOUR\nTI  - Example paper\nAU  - Doe, Jane\nPY  - 2024\nDO  - https://doi.org/10.1000/EXAMPLE.\nAN  - PMID:12345\nER  -\n", encoding="utf-8")
        assignments.write_text(json.dumps({"assignments": [{"section": "Introduction", "paragraph_id": "Introduction-01", "references": [{"doi": "10.1000/example", "priority": "P1", "role": "direct_support"}]}]}), encoding="utf-8")
        records, duplicates = canonical_records([ris]); records, warnings = enrich_assignments(records, load_assignments(assignments)); manifest = write_package(records, duplicates, warnings, output, [ris], assignments)
        assert len(manifest["records"]) == 1 and not warnings and (output / "master.ris").exists()
    print("endnote_bridge self-test passed")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ris", action="append", type=Path, help="Input RIS; repeat for multiple section files", required=False)
    parser.add_argument("--assignments", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("endnote-handoff"))
    parser.add_argument("--library", type=Path)
    parser.add_argument("--dry-run", action="store_true", help="Build package without library mutation (default)")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--apply-sqlite", action="store_true", help="Explicitly enable the macOS private-schema adapter")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test(); return
    if not args.ris:
        parser.error("at least one --ris is required")
    paths = [p.expanduser().resolve() for p in args.ris]
    for path in paths:
        if not path.exists(): parser.error(f"RIS not found: {path}")
    records, duplicates = canonical_records(paths); records, warnings = enrich_assignments(records, load_assignments(args.assignments.expanduser().resolve() if args.assignments else None))
    manifest = write_package(records, duplicates, warnings, args.output_dir.expanduser().resolve(), paths, args.assignments.expanduser().resolve() if args.assignments else None)
    if args.apply:
        if not args.apply_sqlite:
            print("Package created; library unchanged. Add --apply-sqlite explicitly to enable the macOS adapter.")
        elif not args.library:
            parser.error("--library is required with --apply --apply-sqlite")
        else:
            report = apply_sqlite(args.library.expanduser().resolve(), records, args.output_dir.expanduser().resolve())
            manifest["apply_report"] = report
            (args.output_dir.expanduser().resolve() / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
