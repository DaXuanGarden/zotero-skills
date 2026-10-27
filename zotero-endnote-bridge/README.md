# Zotero–EndNote Bridge

This skill turns the RIS and paragraph assignment outputs of `zotero-evidence-review` into a reviewable EndNote handoff. It is designed for a macOS background/scripted workflow:

```text
Zotero evidence review → canonical RIS + assignments
                     → preflight/deduplicate
                     → section / paragraph package
                     → optional EndNote library write
                     → metadata refresh
                     → post-import audit
```

The package writer is platform independent. The library adapter is tested against the macOS EndNote 2025 SQLite layout and is guarded by schema checks. It is opt-in because EndNote's internal format is private.

## Install

From the repository root:

```bash
bash scripts/install-skill.sh --skill zotero-endnote-bridge --target codex --backup
```

## Package and review first

```bash
python3 zotero-endnote-bridge/scripts/endnote_bridge.py \
  --ris intro_references.ris \
  --ris methods_references.ris \
  --ris discussion_references.ris \
  --assignments assignments.json \
  --output-dir endnote-handoff \
  --dry-run
```

The output contains a deduplicated `master.ris`, per-paragraph RIS files under `groups/`, `manifest.json`, `group-map.csv`, and a machine-readable preflight report. Group names follow `Introduction/Introduction-01`, `Methods/Methods-02`, and `Discussion/Discussion-01`. Priorities and roles are retained in RIS `KW` and `N1` fields.

## Apply to a macOS library

Close EndNote first. The explicit `--apply-sqlite` switch is required for a library write:

```bash
python3 zotero-endnote-bridge/scripts/endnote_bridge.py \
  --ris master.ris \
  --assignments assignments.json \
  --library "$HOME/Documents/My EndNote Library.enl" \
  --output-dir endnote-handoff \
  --apply --apply-sqlite
```

The command creates a sibling timestamped backup containing both the `.enl` file and `.Data` directory, refuses a running EndNote process, inserts only new records, annotates matched records, and synchronises the EndNote cache. It leaves unrelated records and groups untouched.

## Metadata and audit

```bash
python3 zotero-endnote-bridge/scripts/endnote_metadata.py \
  --library "$HOME/Documents/My EndNote Library.enl" \
  --apply --refresh-report endnote-handoff/metadata-refresh.json

python3 zotero-endnote-bridge/scripts/endnote_audit.py \
  --library "$HOME/Documents/My EndNote Library.enl" \
  --output endnote-handoff/endnote-audit.json
```

Metadata refresh uses PubMed for PMID records and Crossref for DOI-only records. It does not overwrite populated fields unless `--overwrite` is supplied. The audit checks schema, active record count, required fields, duplicate DOI/PMID identifiers, group membership, and optional metadata comparison against a source RIS.

## What this tool does not promise

It does not infer evidence support, silently choose a citation, or claim that a package build changed EndNote. Inspect the manifest and run the audit after reopening EndNote. When the private database schema is unsupported, keep the generated RIS package and use EndNote's own import command manually.
