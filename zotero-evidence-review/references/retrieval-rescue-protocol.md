# Retrieval Rescue Protocol

This protocol is used when a citation, candidate paper, or claim returns no usable record. It is a
rescue ladder, not permission to broaden the topic until a vaguely related paper appears. Preserve
the claim's anchor concepts throughout the ladder and record every attempted route.

## 1. Identify the failure before changing the query

Classify the first failure as one of:

| Status | Meaning | Next action |
|---|---|---|
| `tool_unavailable` | The required MCP tool is absent or not connected | Report the exact manual query; do not call the route completed |
| `query_error` | The tool returned an error, timeout, or rate limit | Retry once as a separate call after inspecting the error |
| `zero_hits` | The query executed and returned no usable candidate | Move down the identifier/title ladder |
| `metadata_unusable` | A candidate exists but lacks enough inspected metadata | Resolve by identifier or a second source before selection |
| `support_gap` | A real record was inspected but does not support the claim | Preserve the record as a near miss and search a different evidence lane |

Never describe `tool_unavailable`, `query_error`, or `metadata_unusable` as “no literature exists”.
Only `zero_hits` means that a completed query returned no usable hit.

## 2. Use the identifier-first ladder

For a known citation or a paper the user expects to find, try the narrowest stable identifier
first. Stop when the canonical record is resolved; do not create a second record from a less
reliable route.

1. DOI exact match, after removing `https://doi.org/`, spaces, and trailing punctuation.
2. PMID exact match, including a PubMed details lookup when PubMed is available.
3. Zotero citation key or item key exact match.
4. Exact title in quotes, preserving the original language and punctuation-insensitive form.
5. Normalized title: lowercase, Unicode-normalized, punctuation removed, common stopwords retained
   when they distinguish the study.
6. First author + publication year + two to four distinctive title tokens.
7. Title tokens + one population/exposure/outcome anchor.

For steps 4–7, record the normalization or tokens used. Never search an author surname alone or a
gene/method name alone when the original claim has a disease, population, phenotype, or design
constraint.

## 3. Rescue a claim with independent concept lanes

When the citation is unknown or the exact paper is not found, build a claim block and relax one
dimension at a time:

```yaml
claim_id: C01
population_or_object: []
exposure_or_method: []
outcome_or_process: []
design_or_evidence_type: []
context_or_tissue: []
synonyms_and_abbreviations: []
exclusions: []
```

Run separate lanes rather than one query containing every term:

| Lane | Keep fixed | Relax or expand | Purpose |
|---|---|---|---|
| `direct` | population/object + exposure + outcome | spelling and abbreviation variants | Find exact support |
| `phenotype_synonym` | exposure + outcome | phenotype names, legacy terms, controlled vocabulary | Recover renamed constructs, e.g. NAFLD/MASLD |
| `design_method` | exposure + outcome | cohort, GWAS, MR, meta-analysis, guideline terms | Find design-matched evidence |
| `mechanism_context` | outcome + tissue/pathway | mechanism and cell/tissue synonyms | Support plausibility only |
| `related_anchor` | one inspected strong anchor | related/review neighborhood | Expand after a real anchor is found |

The `mechanism_context` and `related_anchor` lanes cannot upgrade a claim to exact direct support.
Keep their evidence level at `C` unless a direct empirical match is subsequently inspected.

## 4. Preserve anchors while broadening

Use progressive relaxation with an explicit reason:

```text
Round 1: exact title/identifier or direct claim query
Round 2: add legacy terms and controlled-vocabulary synonyms
Round 3: remove one non-essential modifier, retain population/object + outcome
Round 4: split exposure and outcome into separate searches, then intersect candidates
Round 5: use related/review discovery from an inspected anchor
```

Do not remove all outcome terms, all population terms, or all design terms in one step. A result
found after dropping the anchors is a discovery lead, not evidence for the original claim.

For biomedical searches, maintain a synonym table before the first retry:

| Concept | Current term | Legacy/controlled terms | Exclusions |
|---|---|---|---|
| disease/phenotype | ... | ... | adjacent disease only |
| exposure/trait | ... | ... | composite lifestyle measure if insomnia is required |
| design | ... | ... | animal-only if human evidence is required |

## 5. Metadata and support recovery are separate

If a title or DOI is found outside Zotero, mark it as `external_discovery` and resolve canonical
metadata before citing or writing RIS. A metadata match does not establish claim support. The record
must still pass the normal metadata/abstract/full-text inspection and receive a source layer and one
A–E evidence level.

If a record is in Zotero but its metadata is incomplete:

1. retrieve the item metadata;
2. resolve DOI/PMID from the item or an available canonical source;
3. re-fetch the canonical record;
4. only then decide `Include`, `Optional`, `Verify`, or `Exclude`.

Never infer missing authors, year, journal, DOI, PMID, or page data from a search snippet.

## 6. Stop, report, and make the gap actionable

Stop a rescue attempt when one of these is true:

- the canonical record is resolved and inspected;
- two consecutive query rounds add no new direct-support candidate;
- the remaining routes would remove a required anchor;
- the tool or access boundary blocks further inspection;
- the user-defined scope or time limit is reached.

Add these fields to the `Recall Audit`:

```yaml
rescue_status: resolved | partial | blocked | no_direct_match
failure_class: tool_unavailable | query_error | zero_hits | metadata_unusable | support_gap
rescue_ladder_used: [doi_exact, title_exact, author_year_tokens]
anchors_preserved: [outcome, population]
queries_not_run: []
manual_next_query: ""
```

`no_direct_match` means completed retrieval and inspection did not find direct support. It is
different from `blocked`, where the search could not be completed.
