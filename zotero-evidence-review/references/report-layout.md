# Evidence Review Report Layout

This layout is the single author-facing information architecture for paragraph evidence packages. It separates the text an author copies, the reasoning used to justify each citation, and the audit records needed to reproduce or import the package.

## Reading order

| Order | Section | Author question answered | What belongs here |
|---:|---|---|---|
| 1 | Metadata and Use Status | What is this package and can I use it? | Scope, date, route, package status, citation style, source status |
| 2 | Critical Warnings | What must I fix before inserting anything? | Only actionable risks: unsupported claim, unverified source, mismatch, duplicate, unavailable tool |
| 3 | Copy-ready Manuscript Text | What can I paste into the manuscript? | Final manuscript language with eligible author–year citations; no audit notes |
| 4 | Claim–Evidence Matrix | Why does each citation belong here? | One row per sentence/claim, including Chinese claim summary and one A–E level |
| 5 | Citation Insertion Sheet | How do I insert it quickly? | One row per placement with anchor, copy-ready citation, search tokens, and canonical record |
| 6 | Annotated Recommended Text | What changed and what is the risk? | Wording rationale, source-layer boundary, caveat, reviewer risk |
| 7 | Diff / Change Log | What changed from my draft? | Phrase-level changes and reasons |
| 8 | Audit Appendix | Can I reproduce and audit this package? | Evidence logic, sentence matrix, support ledger, references, search log, metadata QC, exports |

## Non-duplication rules

- The Claim–Evidence Matrix is the only author-facing explanation of claim-to-citation fit. It must include `主张摘要（中文）` even when the manuscript is English.
- The Citation Insertion Sheet is operational. It may repeat the citation string and identifier, but it must not repeat the full evidence judgment or bibliographic prose.
- The Citation Support Ledger is record-level audit data. It may repeat claim IDs and verdicts, but it must add inspection route, evidence location, and RIS action.
- `SENTENCE_CITATION_MATRIX` and `Citation Placement` belong in the Audit Appendix. They should not introduce a different citation decision from the first three author-facing sections.
- Full titles, journals, DOI, PMID, and Zotero links appear once in the Reference Table or metadata appendix. Other tables use short author–year labels.

## Fixed Claim–Evidence Matrix columns

```text
sentence_id | claim_id | Revised sentence / clause | 主张摘要（中文） |
Recommended citation | Evidence role | Evidence level | Source layer |
Support verdict | insertion_anchor | Manual action
```

`Evidence level` is exactly one of `A`, `B`, `C`, `D`, or `E`. If a sentence contains claims with different levels, split the row by claim or use the most conservative level and explain the split in `Manual action`; never write `A/B` or `A/C`.

## Three-step manual insertion path

1. Copy the manuscript text.
2. In the immediately following matrix, read the Chinese claim summary and confirm the citation's support, level, and anchor.
3. In the insertion sheet, search Zotero/EndNote using `search_tokens` and insert `copy_ready_citation` at the listed anchor.

