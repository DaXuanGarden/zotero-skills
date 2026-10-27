# Safety and backups

`--dry-run` is the default. `--apply` alone only writes the handoff manifest unless `--apply-sqlite` is also present. Before a SQLite mutation the adapter:

1. verifies that the library exists and has the expected `refs` and `groups` tables;
2. checks that EndNote is not running;
3. copies the `.enl` file and sibling `.Data` directory to a timestamped backup;
4. refuses ambiguous DOI, PMID, or fallback identity matches;
5. commits the main database and synchronises the cache only after the transaction succeeds.

The adapter never removes references. To recover, close EndNote, restore both backup components, and reopen the library. Keep the JSON report with the backup path and source package hash.

Metadata writes have a second backup boundary: after the AppleScript completes, close EndNote and run `scripts/endnote_sync.py --apply`. That command backs up the current `.enl` + `.Data` pair and atomically replaces the stale `.enl` copy with the saved `sdb.eni` cache before the final audit.
