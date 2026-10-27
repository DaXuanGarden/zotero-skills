# Troubleshooting

**`EndNote is running`** — close EndNote and retry the SQLite adapter. Use the package RIS manually if the library must remain open.

**`unsupported EndNote schema`** — preserve the generated package and use EndNote's native RIS import. The private schema is release-specific; do not bypass the guard.

**`ambiguous identity`** — inspect the duplicate DOI/PMID in the input and library, resolve it in EndNote, then rerun with a canonical RIS.

**metadata script does not run** — check that the configured application name matches the installed EndNote app. The script is compiled before execution and reports unresolved identifiers; it does not delete records.

**groups are flat after native RIS import** — this is expected: RIS has no portable nested-group protocol. Use the manifest to create the `Introduction`, `Methods`, and `Discussion` sets, or run the opt-in macOS SQLite adapter.
