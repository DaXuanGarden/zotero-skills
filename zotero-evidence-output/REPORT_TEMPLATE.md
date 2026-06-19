# Evidence Review: {topic}

[Back to project summary](./PROJECT_SUMMARY.md)

## 1. Metadata and Use Status

- Project: `{project_name}`
- Manuscript section: `{introduction|results|discussion|limitations|methods|candidate_gene_discussion}`
- Input claim: `{original user claim or paragraph}`
- Generated: `{YYYY-MM-DD HH:MM}`
- Status: `{Ready|Caution|Partial|Superseded|Unknown}`
- Status rationale: `{one sentence explaining the main trigger for this status}`
- Evidence package: `{relative/package/path}`
- Markdown report: `{relative/package/path/evidence_review.md}`
- EndNote RIS: `{relative/package/path/references.ris}`
- PubMed status: `{Completed|Failed; query reported|Partial|Not executed|Tool unavailable; search not executed}`
- Related prior packages: `{none / path + date + topic slug + relationship}`

## 2. Critical Warnings

| Affected claim | Risk | Required action |
|---|---|---|
| `{claim or No critical warnings}` | `{PubMed unavailable / no direct evidence / contradiction / unverified citation or concept / metadata mismatch / duplicate record / current-study vs external-evidence confusion / unsupported causal wording / unsupported BMI-independent claim / unsupported horizontal pleiotropy claim}` | `{revise wording / verify citation / remove claim / complete PubMed search / resolve metadata / deduplicate records / mark as current-study only}` |

If there are no critical warnings, write exactly: `No critical warnings`.

## 3. 核心结论（Bottom Line）

State the evidence-aligned bottom line in 3–6 bullets. Separate what is directly supported from what is plausible, indirect, or a present-study finding.

## 4. 可直接使用的稿件文本（Copy-ready Manuscript Text）

Provide polished manuscript-ready text that can be copied into the manuscript. Remove internal notes, search-process comments, and unverifiable claims. Use cautious wording when support is indirect.

## 5. 注释版推荐文本（Annotated Recommended Text）

| Sentence / clause | Recommended text | Source layer | Evidence level | Citation rationale | Caveat / reviewer risk |
|---|---|---|---|---|---|
| `{sentence}` | `{text}` | `{Current study|Zotero external evidence|PubMed external evidence|Interpretive bridge|Unsupported gap}` | `{A|B|C|D|E}` | `{rationale}` | `{caveat}` |

## 6. 主张—证据矩阵（Claim–Evidence Matrix）

| # | Claim | Source layer | Evidence level | Zotero evidence | PubMed evidence | Evidence status | Confidence | Risk | Recommended action | Recommended citation |
|---|---|---|---|---|---|---|---|---|---|---|
| `1` | `{claim}` | `{Current study|Zotero external evidence|PubMed external evidence|Interpretive bridge|Unsupported gap}` | `{A|B|C|D|E}` | `{citation or none}` | `{PMID/citation or no direct evidence}` | `{supported|partly supported|current-study only|bridge only|gap|needs verification}` | `{High|Medium|Low}` | `{Low|Medium|High}` | `{keep|hedge|move to annotated text|remove|verify|mark as knowledge gap}` | `{citation or none}` |

Evidence levels:

- A = direct evidence for exact claim.
- B = direct evidence for closely related claim.
- C = biological or methodological plausibility only.
- D = current-study finding; external evidence contextual only.
- E = unsupported, contradicted, or requires verification.

## 7. 引文放置建议（Citation Placement）

List recommended sentence-level citation placement. Avoid assigning citations to statements that the cited papers did not test directly.

## 8. Evidence Logic Chain

| Step | Current-study element | External evidence link | Source layer | Evidence level | Inference limit |
|---|---|---|---|---|---|
| `1` | `{your analysis/result}` | `{published support or none}` | `{Current study|Zotero external evidence|PubMed external evidence|Interpretive bridge|Unsupported gap}` | `{A|B|C|D|E}` | `{what can and cannot be inferred}` |

## 9. 参考文献表（Reference Table）

| Short citation | Year | Study type | Main use | Evidence source | Zotero key | DOI | PMID | Key caveat |
|---|---:|---|---|---|---|---|---|---|
| `{Author et al.}` | `{year}` | `{type}` | `{use}` | `{Zotero|PubMed|Zotero + PubMed}` | `{key or —}` | `{doi or —}` | `{pmid or —}` | `{caveat}` |

## 10. Search Reproducibility

| Source | Query | Mode | Max results | Status | Included | Notes |
|---|---|---|---:|---|---:|---|
| `Zotero` | `{semantic query}` | `semantic` | `{n}` | `{Completed|No hits|Failed}` | `{n}` | `{full_text_inspected; included/excluded records}` |
| `PubMed` | `{attempted or planned PubMed query}` | `PubMed` | `{n}` | `{Completed|Failed; query reported|Partial|Not executed|Tool unavailable; search not executed}` | `{n}` | `{included PMIDs; excluded records; failed reason}` |

## 11. Zotero 检索总结（Zotero Search Summary）

| Search route | Query | Hits | Included | Notes |
|---|---|---:|---:|---|
| `{semantic|keyword|tag|collection}` | `{query}` | `{n}` | `{n}` | `{notes}` |

## 12. PubMed 扩展检索（PubMed Expansion）

- Status: `{Completed|Failed; query reported|Partial|Not executed|Tool unavailable; search not executed}`
- Query: `{query}`
- Included PMIDs: `{pmids}`
- Failed or excluded records: `{records and reasons}`

If a query failed, record the failure explicitly and do not treat PubMed expansion as completed.

## 13. 综合写作建议（Integrated Writing Advice）

Explain how to revise the manuscript claim, including what to keep, hedge, remove, or move to a knowledge-gap statement.

## 14. Claims to Revise or Remove

| Claim | Problem | Evidence level | Source layer | Required revision |
|---|---|---|---|---|
| `{claim}` | `{unsupported / overconfident / current-study miscast as external evidence / metadata unresolved}` | `{A|B|C|D|E}` | `{Current study|Zotero external evidence|PubMed external evidence|Interpretive bridge|Unsupported gap}` | `{hedge|remove|verify|move to gap statement}` |

## 15. 证据缺口与审稿风险（Gaps and Reviewer-risk Assessment）

| Affected claim / sentence | Risk | Severity | Evidence basis | Suggested fix |
|---|---|---|---|---|
| `{claim}` | `{risk}` | `{High|Moderate|Low}` | `{source layer and evidence level}` | `{fix}` |

## 16. 元数据质量控制（Metadata Quality Control）

### Reference Canonicalization Gate

| Selected reference | Canonical identifier | DOI | PMID | Title check | First author check | Year check | Canonical Zotero key | Duplicate keys | Duplicate check result | Metadata source of truth | RIS action | Reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `{short citation}` | `{DOI / PMID / Zotero key}` | `{matched / missing / conflict}` | `{matched / missing / conflict}` | `{matched / conflict}` | `{matched / conflict}` | `{matched / conflict}` | `{key or —}` | `{keys or —}` | `{unique / merged / possible duplicate / unresolved duplicate}` | `{PubMed|DOI|Zotero|manual|unknown}` | `{Include|Exclude|Verify|Optional}` | `{reason}` |

### Metadata QC Table

| Reference | Canonical Zotero key | Duplicate/replaced keys | DOI | PMID | Source used for metadata | Metadata warning | RIS action |
|---|---|---|---|---|---|---|---|
| `{short citation}` | `{key or —}` | `{keys or —}` | `{doi or —}` | `{pmid or —}` | `{PubMed|Zotero|DOI|manual|unknown}` | `{warning or none}` | `{include|exclude|optional|verify}` |

## 17. 导出文件（Export File）

- Markdown report: `{relative/path/evidence_review.md}`
- EndNote RIS: `{relative/path/references.ris}`
- Evidence source: Zotero local library and PubMed expansion are separate evidence steps; combined results are deduplicated by DOI/PMID/title when available.
- Package status: `{Ready|Caution|Partial|Superseded|Unknown}`
- Status rationale: `{main trigger for the assigned status}`
- RIS standardization source: `{PMID/PubMed|DOI metadata|Zotero metadata|manual verification}`
- RIS inclusion rule: final recommended citations only; low-relevance hits excluded.
- Metadata warnings: `{missing fields, mismatches, duplicate warnings, or none}`

All paths must be relative. Do not include local absolute paths such as `/Users/...`.

## QA Gate

Run the internal pre-write QA gate before creating/writing Markdown and RIS, then run the post-write QA gate on the written files before reporting success.

Required checks:

- Report contains Status, Critical Warnings, and Copy-ready Manuscript Text.
- Claim–Evidence Matrix contains Evidence level, Source layer, Recommended action, and Recommended citation.
- Current-study findings are not mislabeled as external evidence.
- Direct causality, BMI independence, horizontal pleiotropy, mediation/mechanism, and genetic-prioritization claims are not overconfident unless directly supported.
- PubMed status truthfully reflects actual tool execution; `Completed` requires executed PubMed search plus inspected metadata.
- PubMed-only RIS records come only from completed PubMed searches with inspected metadata.
- Unresolved metadata mismatch and unresolved duplicate records are excluded from RIS.
- RIS contains plain RIS records only, with no Markdown headings or code fences.
- All generated paths are relative.
- Final chat exposes only status, generated relative paths, and critical warnings.
