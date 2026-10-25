# Citation Insertion Sheet

This reference defines the operational handoff for paragraph citation packages. It is separate from the evidence judgment: the Claim–Evidence Matrix decides whether a source supports a claim; this sheet tells the author where and how to insert the eligible citation.

## Default style

Use `author_year` unless the user supplies a journal style or asks for `numbered_vancouver`/`apa_like`. Keep `copy_ready_citation` (what appears in the manuscript) separate from `search_tokens` (what the author types into Zotero or EndNote).

```text
citation_style: author_year
copy_ready_citation: (Mir et al., 2013)
search_tokens: Mir 2013
```

## Required row fields

| Field | Rule |
|---|---|
| `sentence_id` | Stable input sentence ID, such as `S07`. |
| `insertion_anchor` | A clause or sentence ending, such as `after “incident NAFLD”`; “at paragraph end” is insufficient. |
| `copy_ready_citation` | Exact citation string in the selected style. |
| `search_tokens` | Short human-searchable author/year or title terms; never use only a hidden item key. |
| `canonical_record` | The record selected by DOI, PMID, or canonical Zotero key. |
| `PMID` / `DOI` | Identifiers used for deduplication and metadata QC; use `—` when unavailable. |
| `evidence_role` | `direct`, `background`, `method`, `mechanistic`, `bridge`, or `contrasting`. |
| `support_verdict` | One of the Citation Support Ledger values. |
| `RIS_action` | `Include`, `Optional`, `Verify`, or `Exclude`, matching the ledger. |

Create one row per placement. If one paper is used in three sentences, create three placement rows and one row in the global Author–Year Quick Lookup table. Only `Include` and explicitly acceptable `Optional` records may appear in copy-ready text; `Verify` and `Exclude` remain annotated.

## Manual Citation Fast Path

The evidence report is intentionally ordered for manual author–year insertion:

1. Copy the `Copy-ready Manuscript Text`.
2. Read the immediately following `Claim–Evidence Matrix` to confirm the sentence/clause, claim, support verdict, evidence level, and insertion anchor.
3. Search Zotero or EndNote with `search_tokens`, then paste or insert `copy_ready_citation` at the listed anchor.
4. Use this sheet as the final checklist; keep PMID/DOI/Zotero keys for verification and deduplication only.

## User handoff

- Word + Zotero: search `search_tokens`, confirm the canonical author/year record, and insert at `insertion_anchor`.
- EndNote: import the Citation RIS, search `search_tokens` with `Insert Citation`, and let Word/EndNote create final numbering.
- Manual author–year draft: paste `copy_ready_citation` and keep PMID/DOI beside the working notes for audit.

Do not edit a Word field, Zotero item, or EndNote library automatically unless the user explicitly requests that downstream action.
