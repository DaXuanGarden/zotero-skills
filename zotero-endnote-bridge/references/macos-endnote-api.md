# macOS EndNote integration notes

The portable path is RIS package generation. EndNote's AppleScript dictionary exposes `find`, `field`, `set field`, `get records in`, and `set record contents`, but its `import` command is documented around EndNote's own XML interchange in some releases. The bridge therefore does not assume that ordinary RIS can be imported through AppleScript.

For metadata refresh, the bridge generates an ASCII-safe script that uses:

```applescript
set matches to find "30531917" in field "Accession Number"
set field "Title" of record (item 1 of matches) to "..."
```

The application name is configurable with `--endnote-app` and defaults to `EndNote 2025`. The script is compiled with `osacompile` before execution. EndNote should be open for this AppleScript path and closed before the SQLite library adapter path.
