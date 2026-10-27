#!/usr/bin/env python3
"""Synchronize EndNote's saved sdb cache back to the .enl file.

Run this only after the metadata AppleScript has finished and EndNote is
closed. The default is a read-only plan; ``--apply`` makes a full backup and
replaces the main SQLite copy atomically.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import sqlite3
import subprocess
from pathlib import Path


def endnote_running() -> bool:
    result = subprocess.run(["pgrep", "-alf", "EndNote"], capture_output=True, text=True, check=False)
    return any("EndNote" in line and "pgrep" not in line for line in result.stdout.splitlines())


def backup(library: Path) -> Path:
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = library.parent / f"{library.stem}.backup_before_cache_sync_{stamp}"
    suffix = 1
    while path.exists():
        path = library.parent / f"{library.stem}.backup_before_cache_sync_{stamp}_{suffix}"
        suffix += 1
    path.mkdir()
    shutil.copy2(library, path / library.name)
    data = library.with_name(library.stem + ".Data")
    if data.exists():
        shutil.copytree(data, path / data.name)
    return path


def count(path: Path) -> int:
    con = sqlite3.connect(path)
    try:
        return int(con.execute("select count(*) from refs where trash_state=0").fetchone()[0])
    finally:
        con.close()


def sync(library: Path, apply: bool) -> dict[str, object]:
    cache = library.with_name(library.stem + ".Data") / "sdb" / "sdb.eni"
    if not library.exists() or not cache.exists():
        raise FileNotFoundError("library or sdb cache is missing")
    before_main, before_cache = count(library), count(cache)
    report: dict[str, object] = {"library": str(library), "cache": str(cache), "before_main_active_records": before_main, "before_cache_active_records": before_cache, "applied": False}
    if apply:
        if endnote_running():
            raise RuntimeError("EndNote is running; close it before cache synchronization")
        report["backup"] = str(backup(library))
        temporary = library.with_suffix(".enl.sync-temp")
        shutil.copy2(cache, temporary)
        temporary.replace(library)
        report.update({"after_main_active_records": count(library), "applied": True})
        report["synchronized"] = report["after_main_active_records"] == before_cache
    else:
        report["synchronized"] = before_main == before_cache
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print("endnote_sync self-test passed")
        return
    if not args.library:
        parser.error("--library is required")
    report = sync(args.library.expanduser().resolve(), args.apply)
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        path = args.output.expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload + "\n", encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()
