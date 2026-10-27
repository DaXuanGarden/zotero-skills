# Troubleshooting

**`EndNote is running`** — close EndNote and retry the SQLite adapter. Use the package RIS manually if the library must remain open.

**`unsupported EndNote schema`** — preserve the generated package and use EndNote's native RIS import. The private schema is release-specific; do not bypass the guard.

**`ambiguous identity`** — inspect the duplicate DOI/PMID in the input and library, resolve it in EndNote, then rerun with a canonical RIS.

**metadata script does not run** — check that the configured application name matches the installed EndNote app. The script is compiled before execution and reports unresolved identifiers; it does not delete records.

**metadata appears in EndNote but the audit sees old values** — close EndNote and run `endnote_sync.py --apply`. EndNote 2025 can save AppleScript changes in `.Data/sdb/sdb.eni` while `.enl` remains an older SQLite copy.

**groups are flat after native RIS import** — this is expected: RIS has no portable nested-group protocol. Use the manifest to create the `Introduction`, `Methods`, and `Discussion` sets, or run the opt-in macOS SQLite adapter.

**paragraph groups appear under My Groups** — inspect the audit's `my_groups_leaks` field. The current adapter removes bridge-created child IDs from My Groups and exposes only the section sets in EndNote's set list; an old import may need one manual cleanup.
