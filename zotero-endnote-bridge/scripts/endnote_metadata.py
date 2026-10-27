#!/usr/bin/env python3
"""Refresh EndNote metadata with PubMed/Crossref through compiled AppleScript.

The default is a plan. ``--apply`` is required to open EndNote and write
fields; populated values are preserved unless ``--overwrite`` is supplied.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


def clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def pmid(value: Any) -> str:
    return re.sub(r"^(?:pmid|pubmed)\s*:?\s*", "", clean(value), flags=re.I)


def doi(value: Any) -> str:
    return re.sub(r"^https?://(?:dx\.)?doi\.org/", "", clean(value), flags=re.I).rstrip(".").casefold()


def fetch_url(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "zotero-endnote-bridge/1.0"})
    with urllib.request.urlopen(request, timeout=45) as response:
        return response.read()


def fetch_pubmed(identifier: str) -> dict[str, Any]:
    root = ET.fromstring(fetch_url("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" + urllib.parse.urlencode({"db": "pubmed", "id": identifier, "retmode": "xml"})))
    article = root.find(".//PubmedArticle")
    if article is None: return {}
    node = article.find(".//MedlineCitation/Article")
    if node is None: return {}
    authors = []
    for author in node.findall(".//AuthorList/Author"):
        last = clean(author.findtext("LastName")); fore = clean(author.findtext("ForeName") or author.findtext("Initials")); collective = clean(author.findtext("CollectiveName"))
        authors.append(collective or (f"{last}, {fore}" if last and fore else last))
    journal = node.find("Journal")
    year = clean(journal.findtext("JournalIssue/PubDate/Year") if journal is not None else "")
    if not year:
        year = (re.search(r"(?:19|20)\d{2}", clean(journal.findtext("JournalIssue/PubDate/MedlineDate") if journal is not None else "")) or [""])[0]
    ids = {x.attrib.get("IdType", "").casefold(): clean(x.text) for x in article.findall(".//ArticleIdList/ArticleId")}
    return {"pmid": identifier, "doi": doi(ids.get("doi")), "title": clean("".join(node.find("ArticleTitle").itertext()) if node.find("ArticleTitle") is not None else ""), "authors": authors, "year": year, "journal": clean(journal.findtext("Title") if journal is not None else ""), "volume": clean(journal.findtext("JournalIssue/Volume") if journal is not None else ""), "issue": clean(journal.findtext("JournalIssue/Issue") if journal is not None else ""), "pages": clean(node.findtext("Pagination/MedlinePgn")), "url": f"https://pubmed.ncbi.nlm.nih.gov/{identifier}/"}


def fetch_crossref(identifier: str) -> dict[str, Any]:
    data = json.loads(fetch_url("https://api.crossref.org/works/" + urllib.parse.quote(identifier, safe=""))).get("message", {})
    authors = [f"{clean(a.get('family'))}, {clean(a.get('given'))}".rstrip(", ") for a in data.get("author", []) if clean(a.get("family"))]
    dates = data.get("published-print") or data.get("published-online") or data.get("published") or {}
    parts = dates.get("date-parts") or [[]]
    return {"pmid": "", "doi": doi(identifier), "title": clean((data.get("title") or [""])[0]), "authors": authors, "year": str(parts[0][0]) if parts and parts[0] else "", "journal": clean((data.get("container-title") or [""])[0]), "volume": clean(data.get("volume")), "issue": clean(data.get("issue")), "pages": clean(data.get("page") or data.get("article-number")), "url": "https://doi.org/" + doi(identifier)}


def escape_applescript(value: Any) -> str:
    value = str(value or "").replace("\\", "\\\\").replace('"', '\\"').replace("\r", "\\r").replace("\n", "\\r")
    return '"' + value + '"'


def script_for(library: Path, app: str, updates: list[dict[str, Any]], overwrite: bool) -> str:
    lines = [f"tell application {escape_applescript(app)}", f"  open POSIX file {escape_applescript(str(library))}", "  delay 2", f"  set d to document {escape_applescript(library.name)}", "  set changed to 0", "  set unresolved to \"\""]
    for update in updates:
        key_field = "Accession Number" if update.get("pmid") else "DOI"; key = update.get("pmid") or update.get("doi")
        lines += [f"  set matches to find {escape_applescript(key)} in field {escape_applescript(key_field)}", "  if (count of matches) is 1 then", "    set rid to item 1 of matches"]
        fields = [("Title", update.get("title")), ("Author", "\r".join(update.get("authors") or [])), ("Year", update.get("year")), ("Journal", update.get("journal")), ("Volume", update.get("volume")), ("Issue", update.get("issue")), ("Pages", update.get("pages")), ("DOI", update.get("doi")), ("Accession Number", update.get("pmid")), ("URL", update.get("url"))]
        allowed = set(update.get("_fields", [field for field, _ in fields]))
        for field, value in fields:
            if value and (overwrite or field in allowed): lines.append(f"    set field {escape_applescript(field)} of record rid to {escape_applescript(value)}")
        lines += ["    set changed to changed + 1", "  else", f"    set unresolved to unresolved & {escape_applescript(key_field + ':' + str(key) + chr(13))}", "  end if"]
    lines += ["  save", "  return \"UPDATED=\" & changed & \"\\nUNRESOLVED=\" & unresolved", "end tell"]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, required=False)
    parser.add_argument("--app", "--endnote-app", default="EndNote 2025")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite populated EndNote fields with fetched canonical values")
    parser.add_argument("--refresh-report", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        assert 'tell application "EndNote 2025"' in script_for(Path("Library.enl"), "EndNote 2025", [{"pmid": "1", "title": "é"}], False)
        print("endnote_metadata self-test passed"); return
    if not args.library: parser.error("--library is required")
    library = args.library.expanduser().resolve()
    if not library.exists(): parser.error(f"library not found: {library}")
    # Read identifiers directly from the library through the public sqlite
    # fields. This is read-only and lets the refresh be reproducible.
    import sqlite3
    connection = sqlite3.connect(library); connection.row_factory = sqlite3.Row
    rows = connection.execute("select * from refs where trash_state=0").fetchall(); connection.close()
    updates: list[dict[str, Any]] = []; failures: list[dict[str, Any]] = []
    for row in rows:
        identifier = pmid(row["accession_number"])
        try:
            update = fetch_pubmed(identifier) if identifier else fetch_crossref(doi(row["electronic_resource_number"])) if doi(row["electronic_resource_number"]) else {}
            if update:
                field_map = {"Title": "title", "Author": "author", "Year": "year", "Journal": "secondary_title", "Volume": "volume", "Issue": "number", "Pages": "pages", "DOI": "electronic_resource_number", "Accession Number": "accession_number", "URL": "url"}
                update["_fields"] = [field for field, column in field_map.items() if not clean(row[column])]
                updates.append(update)
            else: failures.append({"pmid": identifier, "doi": doi(row["electronic_resource_number"]), "reason": "no canonical identifier or source record"})
        except Exception as exc: failures.append({"pmid": identifier, "doi": doi(row["electronic_resource_number"]), "reason": str(exc)})
    report: dict[str, Any] = {"library": str(library), "app": args.app, "records_seen": len(rows), "updates_prepared": len(updates), "failures": failures, "applied": False, "next_step": "close EndNote and run endnote_sync.py --apply, then run endnote_audit.py"}
    script_path = library.parent / f".zotero_endnote_metadata_{os.getpid()}.applescript"
    compiled_path = library.parent / f".zotero_endnote_metadata_{os.getpid()}.scpt"
    script_path.write_text(script_for(library, args.app, updates, args.overwrite), encoding="utf-8")
    if args.apply:
        compile_result = subprocess.run(["osacompile", "-o", str(compiled_path), str(script_path)], capture_output=True, text=True, check=False)
        if compile_result.returncode:
            report["compile_error"] = compile_result.stderr; raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))
        run_result = subprocess.run(["osascript", str(compiled_path)], capture_output=True, text=True, check=False)
        report.update({"applied": run_result.returncode == 0, "osascript_stdout": run_result.stdout, "osascript_stderr": run_result.stderr})
    report["script"] = str(script_path); report["compiled_script"] = str(compiled_path) if args.apply else None
    if args.refresh_report:
        report_path = args.refresh_report.expanduser().resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.apply and not report["applied"]: raise SystemExit(1)


if __name__ == "__main__":
    main()
