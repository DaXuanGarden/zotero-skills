---
name: zotero-endnote-bridge
description: Safely hand off Zotero evidence-review RIS files and paragraph assignments to macOS EndNote, with deduplication, hierarchical section groups, metadata refresh, backups, and auditable reports.
license: MIT
compatibility: Codex, OpenCode, ZCode (zcode); macOS EndNote 2020–2025 for library writes
metadata:
  workflow: academic-research
  requires: Python 3.9+
  optional: macOS EndNote for --apply-sqlite/metadata refresh
  version: 1.0.0
---

# Zotero–EndNote Bridge Skill

Use this skill after `zotero-evidence-review` has produced a canonical RIS and (when paragraph-aware filing is wanted) an assignment manifest. It creates a deduplicated handoff package, maps references to a two-level EndNote hierarchy, optionally refreshes metadata through PubMed/Crossref, and audits the resulting library.

The bridge deliberately keeps evidence decisions in `zotero-evidence-review`. It does not decide whether a paper supports a claim. It carries the already-reviewed identifiers, paragraph IDs, roles, and priorities into EndNote and preserves an audit trail.

## Safe default workflow

1. Run a preflight/dry run. Input RIS files are never changed.
2. Inspect `manifest.json`, `group-map.csv`, and the per-group RIS files.
3. For an actual library write, close EndNote, create a full `.enl` + `.Data` backup, and use `--apply --apply-sqlite`. The SQLite adapter is explicitly opt-in because EndNote's private schema can change between releases.
4. Refresh metadata only after the import has been audited. Metadata refresh defaults to filling empty fields; `--overwrite` is required to replace non-empty values.
5. Run the post-import audit and keep its JSON report with the manuscript evidence package.

```bash
python3 zotero-endnote-bridge/scripts/endnote_bridge.py \
  --ris references.ris \
  --assignments assignments.json \
  --output-dir handoff \
  --dry-run

python3 zotero-endnote-bridge/scripts/endnote_bridge.py \
  --ris references.ris \
  --assignments assignments.json \
  --library "$HOME/Documents/My Library.enl" \
  --output-dir handoff \
  --apply --apply-sqlite

python3 zotero-endnote-bridge/scripts/endnote_audit.py \
  --library "$HOME/Documents/My Library.enl" \
  --output handoff/endnote-audit.json
```

## Assignment format

```json
{
  "assignments": [
    {
      "section": "Introduction",
      "paragraph_id": "Introduction-01",
      "paragraph_title": "Circadian and MASLD background",
      "references": [
        {"doi": "10.1000/example", "role": "direct_support", "priority": "P1"}
      ]
    }
  ]
}
```

References may be identified by DOI, PMID, Zotero key, or exact title. DOI and PMID are preferred. A record can occur in several paragraphs; the master RIS is still written once, while the manifest records every membership. Unassigned records are retained in `Unassigned/Unassigned` and reported as warnings.

## EndNote-specific boundaries

- RIS is the portable interchange format. Nested EndNote group sets are represented in the manifest and, on macOS, can be materialised by the opt-in SQLite adapter.
- EndNote must be closed before any SQLite write. The adapter checks the schema, refuses ambiguous identifiers, and makes a timestamped backup before mutation.
- EndNote's AppleScript metadata path is separate from the SQLite importer. The script compiles an ASCII-safe AppleScript before execution, because direct Unicode `.applescript` execution is unreliable on some macOS versions.
- The bridge never deletes references. Existing groups with the same names are updated; unrelated groups are left intact.
- A successful package build is not evidence that a library write succeeded. Only the JSON audit after reopening EndNote confirms the final state.

See `README.md`, `references/assignment-schema.md`, `references/macos-endnote-api.md`, `references/safety-and-backups.md`, and `references/troubleshooting.md` for the full contract.
