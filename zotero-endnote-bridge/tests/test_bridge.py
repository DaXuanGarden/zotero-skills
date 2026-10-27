#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sqlite3
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("endnote_bridge", ROOT / "scripts" / "endnote_bridge.py")
assert spec and spec.loader
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)
audit_spec = importlib.util.spec_from_file_location("endnote_audit", ROOT / "scripts" / "endnote_audit.py")
assert audit_spec and audit_spec.loader
audit_module = importlib.util.module_from_spec(audit_spec)
audit_spec.loader.exec_module(audit_module)


def main() -> None:
    fixture = ROOT / "tests" / "fixtures"
    with tempfile.TemporaryDirectory() as directory:
        out = Path(directory) / "handoff"
        records, duplicates = bridge.canonical_records([fixture / "sample.ris", fixture / "sample.ris"])
        assert len(records) == 2 and len(duplicates) == 2
        variant = Path(directory) / "variant.ris"
        variant.write_text("TY  - JOUR\nTI  - DOI only example (online)\nAU  - Brown, Carol\nPY  - 2023\nDO  - 10.1000/doi-only\nER  -\n", encoding="utf-8")
        merged, merged_duplicates = bridge.canonical_records([fixture / "sample.ris", variant])
        assert len(merged) == 2 and len(merged_duplicates) == 1, "DOI duplicates must collapse even when titles differ"
        same_title = Path(directory) / "same-title.ris"
        same_title.write_text("TY  - JOUR\nTI  - DOI only example\nAU  - Brown, Carol\nPY  - 2023\nDO  - 10.1000/second-doi\nAN  - 99999\nER  -\n", encoding="utf-8")
        separate, separate_duplicates = bridge.canonical_records([fixture / "sample.ris", same_title])
        assert len(separate) == 3 and not separate_duplicates, "distinct canonical identifiers must survive a title collision"
        records, warnings = bridge.enrich_assignments(records, bridge.load_assignments(fixture / "assignments.json"))
        assert not warnings
        legacy = Path(directory) / "legacy.json"
        legacy.write_text(json.dumps({"assignments": [{"section": "Introduction", "paragraph_id": "Paragraph 1", "references": []}]}), encoding="utf-8")
        assert bridge.load_assignments(legacy)[0]["paragraph_id"] == "Introduction-01"
        invalid = Path(directory) / "invalid.json"
        invalid.write_text(json.dumps({"assignments": [{"section": "Methods", "paragraph_id": "Paragraph 1", "references": []}]}), encoding="utf-8")
        try:
            bridge.load_assignments(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("strict assignment validation must reject a generic Methods paragraph")
        manifest = bridge.write_package(records, duplicates, warnings, out, [fixture / "sample.ris"], fixture / "assignments.json")
        assert len(manifest["groups"]) == 2
        assert (out / "groups" / "Introduction__Introduction-01.ris").exists()
        text = (out / "master.ris").read_text(encoding="utf-8")
        assert "Manuscript group: Introduction/Introduction-01" in text
        assert json.loads((out / "manifest.json").read_text(encoding="utf-8"))["schema_version"] == "1.0"
        library = Path(directory) / "fixture.enl"
        connection = sqlite3.connect(library)
        connection.execute("create table refs (id integer primary key, title text, author text, year text, secondary_title text, volume text, number text, pages text, accession_number text, electronic_resource_number text, url text, trash_state integer, keywords text, research_notes text)")
        connection.execute("create table groups (group_id integer, spec blob, members blob)")
        connection.execute("create table misc (code integer, subcode integer, value blob, primary key(code, subcode))")
        connection.execute("insert into refs values (1, 'Example', 'Doe, Jane', '2024', 'Journal', '1', '1', '1-2', '12345', '10.1000/example', 'https://doi.org/10.1000/example', 0, '', '')")
        spec_blob, group_id = bridge.group_spec("Introduction / Introduction-01", 1)
        set_blob, set_id = bridge.groupset_xml("Introduction", [group_id], 1)
        connection.execute("insert into groups values (1, ?, ?)", (spec_blob, bridge.member_blob([1])))
        connection.execute("insert into misc values (17, 1, ?)", (b'<groupset version="1"><ids><id>MY</id><name>My Groups</name></ids><members complex="true"></members></groupset>',))
        connection.execute("insert into misc values (17, 100, ?)", (set_blob,))
        connection.execute("insert into misc values (18, 0, ?)", (f'<setlist version="1"><sets><set collapsed="false">{set_id}</set></sets></setlist>'.encode(),))
        connection.commit(); connection.close()
        connection = sqlite3.connect(library)
        same_id, same_subcode, created = bridge.upsert_section_group_set(connection, "Introduction", [group_id], 2)
        assert same_id == set_id and same_subcode == 100 and not created
        connection.execute("update misc set value=? where code=17 and subcode=1", (f'<groupset version="1"><ids><id>MY</id><name>My Groups</name></ids><members complex="true"><member>{group_id}</member><member>OTHER</member></members></groupset>'.encode(),))
        assert bridge.remove_from_my_groups(connection, {group_id})
        connection.commit(); connection.close()
        audit_manifest = Path(directory) / "audit-manifest.json"
        audit_manifest.write_text(json.dumps({"groups": [{"section": "Introduction", "paragraph_id": "Introduction-01"}]}), encoding="utf-8")
        report = audit_module.audit(library, manifest=audit_manifest)
        assert report["status"] in {"pass", "warn"} and report["checks"]["active_records"] == 1
        assert report["checks"]["group_policy"]["status"] == "pass"
    print("zotero-endnote-bridge tests passed")


if __name__ == "__main__":
    main()
