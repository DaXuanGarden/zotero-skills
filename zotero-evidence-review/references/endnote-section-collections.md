# Section- and paragraph-aware EndNote handoff

Use this handoff when a manuscript paragraph, section, claim block, or evidence package needs a durable reference classification such as:

```text
Introduction/
  Introduction-01/
Methods/
  Methods-01/
Results/
  Results-02/
Discussion/
  Discussion-01/
  Discussion-02/
```

## Assignment contract

The evidence workflow supplies a JSON assignment file. Each assignment has:

```json
{
  "section": "Discussion",
  "paragraph_id": "Discussion-01",
  "claim_ids": ["C01"],
  "references": [
    {
      "doi": "10.xxxx/example",
      "role": "direct_support"
    }
  ]
}
```

Use a canonical DOI, PMID, Zotero key, or exact title to resolve a reference against the metadata-checked source RIS. Do not assign a record by an unverified author-year string when a canonical identifier is available.

## Generated package

Run:

```bash
python3 scripts/write_endnote_collection_package.py \
  --ris path/to/canonical_references.ris \
  --assignments path/to/assignments.json \
  --output-root zotero-evidence-output
```

The package contains:

- one master RIS containing every source record exactly once;
- `KW` fields for `Manuscript section`, `Manuscript paragraph`, `Manuscript group`, `Claim`, and `Evidence role`;
- `endnote-import/{Section}/{Paragraph}.ris` selective handoffs;
- a JSON collection manifest;
- a Markdown manuscript-to-reference map.

Import the master RIS once to avoid duplicates. The per-group RIS files are for selective import or audit. RIS has no portable nested EndNote-group protocol, so the group hierarchy is preserved in keywords and the manifest. EndNote Smart Groups can filter on `Manuscript group: Discussion/Discussion-01`; otherwise create the custom groups once using the manifest.

## Assignment rules

- One paragraph gets one stable `paragraph_id`, for example `Discussion-01`.
- A reference can belong to several paragraphs; the master RIS remains deduplicated and receives all group keywords.
- Use roles such as `direct_support`, `background`, `method`, `interpretive_bridge`, and `optional`.
- Unassigned source records are retained under `Unassigned/Unassigned` so the package never silently drops a confirmed citation.
- The package writer does not search, infer support, or modify `.enl`, `.Data`, or other EndNote-owned files.
