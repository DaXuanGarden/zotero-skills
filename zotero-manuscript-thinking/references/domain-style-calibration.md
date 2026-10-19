# Domain-Native Style Calibration

This reference defines how to use high-quality peer papers as a writing calibration set. It is a
pattern-extraction workflow, not a copying or journal-acceptance prediction workflow.

## 1. Define the target before reading exemplars

Record the following fields before selecting papers:

```text
domain: <field and subfield>
article_type: <original research / review / methods / brief report / thesis chapter>
target_venue: <journal or conference, or unspecified>
section: <Introduction / Methods / Results / Discussion / ...>
audience: <specialists / broad scientific readers / clinical readers>
language: <Chinese / English / bilingual>
author_constraints: <terms, claims, numbers, citations, and scope that must remain fixed>
```

If `target_venue` is unknown, use a genre-neutral peer profile and say so. Do not silently apply
Nature, a top conference, or another venue's conventions merely because they sound prestigious.

Section-specific calibration must follow the function of the section. A paper can be a useful
language exemplar for one section and a poor exemplar for another; do not transfer an Introduction
pattern into Methods or a Discussion pattern into Results without recording the boundary.

## 2. Build a small, inspectable peer corpus

Prefer 3–5 papers. Select them in this order:

1. same section and article type;
2. same subfield, method family, population or phenomenon;
3. target venue or a clearly adjacent venue;
4. a recent representative paper plus a field-defining paper when both are available.

For every paper, record:

| Peer ID | Citation/DOI/PMID | Venue/year | Match rationale | Material inspected | Access status | Use in calibration |
|---|---|---|---|---|---|---|
| P1 | ... | ... | ... | full text / section / abstract | inspected / partial / unavailable | ... |

Use Zotero first when the paper is already in the user's library. Use PubMed or another enabled
source only when available and report the actual inspection level. A title or search snippet is a
discovery lead, not evidence of a writing pattern. If fewer than three suitable papers are
inspectable, set `calibration_confidence: low` and do not describe the result as field consensus.

## 2A. Zotero-native retrieval and fragment inspection

When this Skill runs through `zotero-evidence-review`, use the user's Zotero library as the
primary style corpus. The retrieval chain is sequential because every downstream call depends on
keys returned by the previous call:

1. Run the read-only connection smoke test with `zotero_get_recent(limit=3)`. If Zotero MCP is
   unavailable or not connected, stop the Zotero style-corpus chain and report
   `Zotero MCP visible but not connected` or `⚠️ Tool unavailable; search not executed`.
2. Expand the user's target into one semantic query containing the domain, phenomenon/method,
   article type and section. Run `zotero_semantic_search` first; inspect the returned titles,
   item keys, collections and relevance before choosing papers.
3. If the pool is too small or poorly matched, run one separate `zotero_search_items` or
   `zotero_advanced_search` keyword fallback. Do not schedule fallback, metadata, or PDF calls in
   the same batch as the first search.
4. For selected candidates, call `zotero_get_item_metadata` and record the canonical title,
   authors, year, journal, DOI/PMID, item key and any user-provided venue/selection rationale.
5. Locate attachments with `zotero_get_item_children` or `zotero_get_items_children`. Prefer a
   PDF attachment; record its attachment key and `zotero://open-pdf/library/items/{attachment_key}`
   link. A metadata-only record cannot establish a full-text style pattern.
6. Locate the relevant section with `zotero_get_pdf_outline` when available. Prefer the parent
   item key for outline/page resolution because some local Zotero bridges list an attachment key
   but cannot resolve that key to a file; use the attachment key only when the bridge confirms it
   is readable. Then read only the relevant pages with `zotero_read_pdf_pages`; use
   `zotero_get_item_fulltext` as a documented fallback when page reading is unavailable. Record
   section/subsection and physical PDF page when available, or mark the location as
   `fulltext fallback / page unavailable`.
7. Store a short source fragment only when needed to make the pattern auditable. Keep the fragment
   minimal, preserve the source language, and pair it with an abstraction; never paste a peer's
   paragraph into copy-ready manuscript text.

The chain must stop after the first failed upstream call. A skipped downstream call is
`not executed`, not a zero-hit or missing-PDF result. Treat a textual `Error`, `Code:`, `502`,
or equivalent failure in `result` as a failed call even if the transport wrapper reports
`isError: false`. Retry a failed or empty search at most once, as a separate call, after
inspecting the error or result; a PDF read failure may instead use the documented full-text
fallback. Do not read annotations or notes as a substitute for the article's prose unless the
user explicitly asks for a notes-based corpus.

Use this ledger for each inspected fragment:

```markdown
| Peer ID | Zotero item/attachment | Query or selection reason | Section | PDF page | Short source fragment | Abstracted pattern | Applicability | Inspection status |
|---|---|---|---|---:|---|---|---|---|
| P1 | ... | ... | Introduction, para. 3 | 2 | ... | ... | adopt_move / do_not_adopt | full / partial / metadata-only |
```

`full` means the relevant section was read from the PDF or full text; `partial` means only some
pages or an abstract were available; `metadata-only` means the record was selected but supplies no
style evidence. Only `full` fragments can support a `high` calibration confidence.

## 3. Extract patterns, not prose

For each peer, record short, location-bound observations in these categories:

- **rhetorical moves**: how the section opens, narrows the gap, introduces the method, states a
  result, compares with prior work, handles a limitation, and closes an implication;
- **sentence functions**: what the subject and verb do in a typical claim, comparison, or hedge;
- **claim calibration**: recurring evidence-matched verbs and where uncertainty is retained;
- **information rhythm**: approximate sentence length variation, number of claims per paragraph,
  and where technical detail is deferred;
- **terminology**: conventional field terms, abbreviation timing, spelling, tense and unit norms;
- **citation ownership**: whether a citation supports background, a prior finding, a method, or a
  contrast, and how close it sits to the supported claim;
- **reader path**: what a reader must know before each paragraph and what question the next
  paragraph answers.

For **Methods**, additionally extract the order in which the paper introduces design, setting,
participants/samples, variables, procedures, quality control, statistics and ethics; how it marks
completed actions versus planned analyses; how it reports units, thresholds, software versions and
replicate structure; and which details are deferred to supplements. The safe abstraction should
describe a reproducibility move, such as “defines the analysis population before naming the model,”
not copy a protocol sentence.

For **Results**, additionally extract the order of descriptive setup, primary findings, supporting
analyses, sensitivity/subgroup analyses and validation; how paragraphs open with a reader-facing
rationale and then a quantitative anchor; how figures/tables are cited; and where the paper stops
before interpretation. A safe abstraction might be “states the comparison and estimate before the
uncertainty interval, then points to the corresponding panel,” while preserving the user's own
numbers and direction.

Do not copy a peer's sentence, distinctive phrase, data, claim, or rhetorical flourish into the
manuscript. Keep any quoted source text to the minimum needed to document a pattern, with a
citation and location. The deliverable should be an abstraction such as “paragraph opens with a
measured unresolved relationship, then groups prior studies by method family,” followed by a safe
rewrite of the user's own claim.

## 4. Compare the draft against the profile

Use a contrastive table:

```markdown
| Pattern ID | Peer pattern and source | Draft location | Mismatch | Safe action | Meaning check |
|---|---|---|---|---|---|
```

Allowed actions are `adopt_move`, `reorder`, `clarify_subject`, `calibrate_verb`,
`replace_nonstandard_term`, `compress_repetition`, `add_bridge`, `retain`, and `do_not_adopt`.
`do_not_adopt` is required when a peer pattern depends on a different study design, audience,
language, venue, or evidence level.

The final copy-ready text must be written from the user's claims and evidence. The peer corpus may
justify why a move or term is conventional, but it cannot supply a missing result, contribution,
citation, or limitation.

## 5. Confidence and stopping rules

Report one of:

- `high`: at least three closely matched papers, the relevant section was inspected, and the same
  pattern appears across papers;
- `medium`: at least three papers were inspected, but venue, section, or article type is mixed;
- `low`: fewer than three relevant papers, abstract-only inspection, or substantial access gaps;
- `none`: no inspectable corpus; give a genre-neutral edit and state that corpus calibration was not
  performed.

Stop adding papers when a new paper only repeats an existing pattern, changes no action, or pulls
the draft toward a different genre. A style pass is complete when the profile names the target,
every recommended change has a source or an explicit genre rationale, claim strength and
terminology remain stable, and the author can see which choices still require approval.

## 6. Required output block

When calibration is requested, append this block to the manuscript review:

```markdown
## Domain Style Calibration
- target_profile: ...
- corpus_status: inspected / partial / unavailable
- calibration_confidence: high / medium / low / none
- peer_corpus: P1 ...; P2 ...; P3 ...

### Observed patterns
| Pattern ID | Section/job | Peer evidence | Pattern | Boundary |
|---|---|---|---|---|

### Draft-to-profile comparison
| Pattern ID | Draft location | Mismatch | Safe action | Meaning check |
|---|---|---|---|---|

### Author decisions
- Keep: ...
- Confirm: ...
- Do not adopt: ...
```

Do not call the result “high-score style” unless the user supplies a defensible selection criterion.
Prefer “matched peer corpus” or “target-venue calibration.”
