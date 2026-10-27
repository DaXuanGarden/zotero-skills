# Recall-first retrieval and EndNote handoff

This reference defines the completeness-oriented retrieval layer for paragraph citation work. It is a high-recall protocol, not a promise of mathematically complete literature coverage. The report must show what was searched, what was screened, what was missed, and why the final references were selected.

## 1. Separate recall from selection

Do not stop when the first relevant paper is found. Run discovery broadly, then select narrowly:

```text
claim decomposition
  → independent retrieval lanes
  → candidate pooling and DOI/PMID deduplication
  → directness/quality/full-text screening
  → best-support set
  → canonical metadata
  → one RIS export
```

The final RIS is a selected citation set. The Markdown report retains the broader candidate pool, near misses, exclusions, and unresolved gaps so that “not selected” is not confused with “not found.”

## 2. Claim blocks and retrieval lanes

When an expected citation is missing, apply the identifier-first and progressive-relaxation ladder in
[retrieval-rescue-protocol.md](retrieval-rescue-protocol.md) before broadening the topic. A failed
exact query is a retrieval event to classify, not evidence that the paper does not exist.

For every manuscript claim, record these blocks before searching:

```yaml
claim_id: C01
claim_text: ""
population_or_object: []
exposure_or_method: []
outcome_or_process: []
design_or_evidence_type: []
context_or_tissue: []
synonyms_and_abbreviations: []
exclusions: []
```

Use independent lanes rather than one over-constrained query:

| Lane | Required action | Purpose |
|---|---|---|
| `zotero_semantic` | One natural-language semantic query | Recall conceptually similar items already in the local library |
| `zotero_structured` | One short keyword/advanced/collection query using the same blocks | Recover items missed by embeddings and constrain by metadata |
| `pubmed_broad` | MeSH + title/abstract synonym query | Broad biomedical recall outside Zotero |
| `pubmed_design_or_method` | Design, method, or population-specific query | Recover method- or design-matched studies |
| `pubmed_related` | `pubmed_find_related` for one or two strong anchors when available | Citation-neighborhood expansion, not a substitute for Boolean search |

Run each dependent MCP call sequentially. Record query text, date, result count, inspected count, and failure status for every lane. Do not claim a lane ran when its tool was unavailable or skipped after an upstream failure.

## 3. Saturation and coverage audit

Use a practical stopping rule:

1. Run at least one semantic and one structured Zotero lane.
2. When PubMed is available, run at least two independent PubMed query families (`broad` and `design_or_method`); add `related` for a strong anchor when comprehensive coverage is requested.
3. Deduplicate by DOI, then PMID, then normalized title + first author + year. Keep all retrieval lanes in `retrieved_by` even after merging.
4. Continue one query revision when a lane returns zero, is obviously noisy, or introduces new direct-support candidates.
5. Stop only after two consecutive query rounds add no new direct-support candidate and no new concept block, or when the user-defined scope/time limit is reached.

Report these fields:

```yaml
recall_status: saturated | partial | blocked | scope_limited
query_families_run: 0
raw_hits: 0
unique_candidates: 0
inspected_candidates: 0
direct_support_candidates: 0
new_direct_candidates_last_round: 0
coverage_gaps: []
reason_for_stop: ""
```

`saturated` means the stopping rule was met within the declared scope; it does not mean that no paper exists outside the searched databases, language, date range, or access boundary. If PubMed is unavailable, use `partial` or `blocked`, never `saturated`.

## 4. Screening and provenance

Every pooled candidate gets one row with:

```yaml
candidate_id: K01
claim_ids: [C01]
retrieved_by: [zotero_semantic, pubmed_broad]
canonical_key: doi:10.xxxx/xxxxx | pmid:12345678 | titlehash:...
source_provenance: Zotero | PubMed | Zotero + PubMed
relevance: direct | adjacent | background | noise
support_verdict: yes | partial | no | unverified | contradictory
fulltext_status: inspected | partial | abstract-only | unavailable
selection_action: Include | Optional | Exclude | Verify
exclusion_reason: ""
```

Rank the final set by directness to the claim, evidence design, population/context match, metadata confidence, and full-text inspectability. Do not rank only by semantic similarity, recency, journal prestige, or citation count.

## 5. PubMed-only records and optional Zotero import

PubMed-only records do not have a Zotero item key. Keep their DOI/PMID and set `zotero_import_status: pending`; never invent a Zotero item key or a `zotero://select/items/...` link. If the user explicitly requests Zotero synchronization for selected records, use `zotero_add_by_doi` when a DOI is available, then run `zotero_update_search_database` and re-fetch `zotero_get_item_metadata` before returning the new key. This is an explicit library-write action and is outside the default read-only retrieval path.

```markdown
## ZOTERO_IMPORT_HANDOFF
| Candidate | DOI / PMID | Zotero item key | zotero_import_status | Action |
|---|---|---|---|---|
| Author Year | DOI / PMID | pending | pending / imported / failed | import by DOI only after explicit request |
```

## 6. EndNote import handoff

The canonical output is a plain UTF-8 RIS file. Before handoff:

1. Run `python3 scripts/ris_lint.py <ris-file> --fail-on-warnings`.
2. Confirm every `Include`/`Optional` record has a canonical DOI, PMID, or inspected Zotero key and no unresolved metadata conflict.
3. Write an `ENDNOTE_IMPORT_HANDOFF` block containing the RIS path, record count, deduplication rule, RIS linter result, and the exact user action.
4. Let the user import the RIS in EndNote (`File → Import → File`, the RIS/EndNote import filter, UTF-8) and confirm the destination library. Never edit `.enl`, `.Data`, `sdb.eni`, or EndNote-owned files directly.

`format-references-endnote` may be used after this step when a Markdown manuscript contains explicit `[PMID: ...]` markers and the user wants a Word/CWYW handoff. It is a document/placeholder converter, not the discovery or canonicalization layer; it must not replace a mixed Zotero + PubMed RIS with a PubMed-only re-fetch when Zotero-only records are included.

`endnote-workflow` is a separate two-phase Windows/EndNote 20 workflow for supplied DOCX files and a read-only library. `bib-formatter` can validate or reformat RIS, but it does not import records into EndNote. These boundaries must be stated in the report.

## 7. Required report block

```markdown
## Recall Audit
- recall_status: saturated / partial / blocked / scope_limited
- scope: ...
- query_families_run: ...
- raw_hits: ...
- unique_candidates: ...
- inspected_candidates: ...
- direct_support_candidates: ...
- new_direct_candidates_last_round: ...
- coverage_gaps: ...
- reason_for_stop: ...

| Query ID | Lane | Query | Tool status | Raw hits | New unique IDs | New direct candidates | Action |
|---|---|---|---|---:|---:|---:|---|
| Q01 | zotero_semantic | ... | Completed / Failed / Not executed | ... | ... | ... | retain / revise / stop |
```

```markdown
## ENDNOTE_IMPORT_HANDOFF
- ris_path: ...
- record_count: ...
- included_records: ...
- optional_records: ...
- excluded_or_verify_records: ...
- deduplication_rule: DOI → PMID → normalized title + first author + year
- ris_lint: passed / failed / not run
- canonical_metadata_sources: PMID/PubMed / DOI / Zotero
- import_action: User imports the UTF-8 RIS into the selected EndNote library
- direct_library_write: not supported; no `.enl`/`.Data` files modified
- optional_document_handoff: format-references-endnote only when explicit `[PMID: ...]` markers are present
```
