---
name: zotero-evidence-review
description: Search, analyze, verify, and export Zotero-grounded evidence packages with Markdown evidence reports and EndNote-compatible RIS references. Requires Zotero MCP to be configured.
license: MIT
compatibility: opencode,zcode
metadata:
  workflow: academic-research
  requires: zotero-mcp
  optional: pubmed-mcp
  version: 2.8.0
---

# Zotero Evidence Review Skill

## Overview

Use Zotero MCP tools to search the user's Zotero library intelligently, and use PubMed MCP tools as a biomedical expansion and metadata-standardization layer whenever they are visible in the active Agent IDE session. This skill combines **semantic search** (concept matching via embeddings) with **keyword/structured search**, performs **paragraph evidence and citation analysis** from draft text, verifies **citations against full text**, and can generate a two-file **Evidence Package** for writing workflows: a Markdown evidence report plus an EndNote-compatible RIS reference file.

For paragraph citation-support requests, the default is one complete **Paragraph Citation Package Workflow** rather than two separate workflows: paragraph → claim extraction → one Zotero local search pass → evidence matrix → citation placement → revised/diff paragraph → Zotero metadata + PDF links → automatic PubMed expansion as a second evidence source when available → combined evidence synthesis and deduplication → reference export standardization by PMID/DOI → metadata QC → Markdown evidence report → EndNote RIS. Chat-only paragraph analysis is an explicit opt-out mode.

---

## 0. Intent Detection

Route the user's request before choosing tools. Use the input shape and explicit trigger words; do not ask the user to choose a mode when the intent is clear.

| Intent | User input features | Route to |
|--------|---------------------|----------|
| `search` | Keywords, concepts, natural-language questions, broad topic discovery, or requests such as "search", "find papers", "what literature do I have about…" | **Module 1: Semantic + Structured Search** |
| `paragraph` | A pasted manuscript paragraph, draft section, or multi-sentence passage that asks for chat-only evidence analysis, with no citation/export/full-workflow trigger | **Module 2: Paragraph Evidence & Citation Analysis** |
| `package` | Requests using `/zotero-evidence-review`, saved files, EndNote/RIS export, evidence package, "使用技能", "完整工作流", "找证据", "找引文", "补引用", "推荐引用", "citation", "refs", "参考文献", "文献引用", "生成报告", "保存结果", "导出参考文献", or a paragraph/search request that asks for citation placement, reusable writing outputs, or file outputs | **Paragraph Citation Package Workflow (Module 2 + Module 2.5): analysis stage, then export stage with automatic PubMed expansion after Zotero local search when available** |
| `verify` | Words such as "verify", "核实", "check", "confirm" plus a specific citation/paper and a concrete claim, quote, statistic, or citation-supported statement | **Module 3: Citation Verification Protocol** |
| `health` | "library status", "库状态", "health check", "健康检查", "preflight", "index status", or questions about Zotero database readiness | **Module 0.5: Library Health Check** |

### Routing Rules

1. **Slash command and simple-request entry**: `/zotero-evidence-review` is the recommended user-facing entry point. Treat it as a request to run this skill and auto-route from the user's short request; do not require the user to name modules or repeat the full workflow. When the short request asks for evidence, citation support, reusable writing output, or an evidence package, default to the complete package workflow and write the report/RIS unless the user explicitly opts out.
2. **Paragraph-first, package by default for citation work**: if the user provides a paragraph, run Module 2 first. If the same request includes `/zotero-evidence-review`, `使用技能`, `完整工作流`, "find evidence", "find/add/recommend citations", `找证据`, `找引文`, `补引用`, `推荐引用`, `citation`, `refs`, `参考文献`, `文献引用`, or any request for saved/reusable writing outputs, continue automatically to the Paragraph Citation Package Workflow / Module 2.5 and write the Markdown report plus RIS file.
3. **Chat-only opt-out**: if the user explicitly says `只在聊天输出`, `不要生成文件`, `不导出`, `chat only`, or equivalent, stop after the relevant chat workflow and do not write package files.
4. **Verification requires specificity**: only route to `verify` when both a cited source (or item key/DOI/title) and a claim/quote/statistic are present. Otherwise, route to `search` or ask a clarification.
5. **Health check is read-only by default**: route health/status requests to Module 0.5 and do not run repair actions unless the user explicitly confirms them.
6. **Evidence package request**: if the user asks for saved reports, EndNote/RIS, an evidence package, or the default citation-support workflow above, run the underlying search/paragraph workflow first, then route to the Paragraph Citation Package Workflow / Module 2.5 for file generation.
7. **Ambiguous intent**: if the request cannot be confidently routed, output this numbered menu and ask the user to choose:

```markdown
我可以按以下哪种方式处理？
1. 语义+结构搜索（关键词/概念/问句）
2. 段落证据与引文分析（粘贴段落、找证据、补引用）
3. Evidence Package 导出（Markdown 报告 + EndNote RIS）
4. 精确核实（具体引用 + 具体主张/数据/引文）
5. 库健康度检查（库状态、索引、PDF覆盖率）
```

### End-to-End Workflow Map

Use this map as the default execution path so the workflow remains continuous and auditable:

```text
intent routing → optional read-only library readiness check → Module 1 search or Module 2 paragraph analysis → Zotero canonical metadata + PDF links → automatic PubMed expansion as a second evidence source when available → combined evidence synthesis and deduplication → reference export standardization by PMID/DOI → metadata QC → Markdown evidence report + EndNote RIS → final path-only summary
```

Operational checkpoints:

1. **Before searching**: identify scope, language, explicit opt-out, and whether the request is chat-only or the full **Paragraph Citation Package Workflow (Module 2 + Module 2.5)**.
2. **Before MCP-dependent work**: apply **0.25 MCP Readiness and Runtime Availability**. Zotero MCP is required for local evidence work; PubMed MCP is optional and can only be used when a PubMed/NCBI-capable callable tool is visible in the active session.
3. **During Zotero work**: search Zotero first, deduplicate candidate evidence, and retrieve inspected metadata before using an item in a report or RIS record.
4. **During PubMed work**: when PubMed tools are visible, use `pubmed_search` for expansion, `pubmed_get_details` or `pubmed_extract_info` for selected PMIDs, `pubmed_find_related` for key-paper expansion, and `pubmed_detect_fulltext` / `pubmed_download_fulltext` only for OA full text when enabled and useful.
5. **Before PubMed claims**: only mark PubMed as `Completed` if a PubMed-capable tool is configured and visible, the PubMed search actually ran, and selected PMID metadata was inspected. Otherwise report the query with `⚠️ Tool unavailable; search not executed`, `Failed; query reported`, or `Not executed` with reason.
6. **Before PubMed-only RIS**: include PubMed-only records only when PubMed status is `Completed` and metadata has been inspected with `pubmed_get_details`, `pubmed_extract_info`, or an equivalent visible PubMed metadata tool.
7. **Before writing files**: run metadata quality checks for missing fields, possible Zotero/PubMed mismatch, duplicate warning, and RIS inclusion/exclusion action.
8. **Before final response**: confirm the Markdown report follows `EVIDENCE_REVIEW_REPORT`, the RIS is plain RIS records only, and the chat response lists only generated paths plus critical warnings.

---

## 0. Durable Output Language Policy

Use a Chinese-first durable report by default whenever the user writes in Chinese or does not explicitly request an English-only report. This policy applies to saved Markdown evidence reports and final chat summaries; it does not localize official bibliographic metadata or RIS syntax.

| Output component | Default language / format |
|------------------|---------------------------|
| User-facing report headings, explanations, synthesis, warnings, gap analysis, reviewer-risk notes, metadata QC explanations | Chinese |
| English manuscript paragraphs or manuscript fragments supplied by the user | Preserve English; polish in English unless translation is explicitly requested |
| Chinese manuscript paragraphs | Preserve Chinese; revise in Chinese unless translation is explicitly requested |
| Article titles, journal names, author names, DOI, PMID, Zotero item keys, database names, URLs, and official metadata | Keep official/original form, usually English |
| PubMed execution status values | Keep machine-recognizable values such as `Completed`, `⚠️ Tool unavailable; search not executed`, and `Failed; query reported`, with Chinese explanation nearby when useful |
| EndNote RIS file | Plain standard RIS only; RIS field tags and bibliographic metadata must not be translated or wrapped in Markdown |

Rules:

- The saved `EVIDENCE_REVIEW_REPORT` should be readable as a Chinese research workflow report: Chinese section titles, Chinese analytical prose, Chinese caveats, and Chinese QC notes.
- Do not force English manuscript polishing into Chinese. If the draft paragraph is English, the recommended manuscript text and diff paragraph may remain English while the evidence explanation around it is Chinese.
- Do not translate official paper titles, journal names, author names, DOI, PMID, or RIS fields unless the user explicitly asks for a separate human-readable translation outside the RIS file.
- Never localize RIS tags (`TY`, `AU`, `TI`, `JO`, `DO`, `ER`, etc.) and never add Chinese explanations, Markdown headings, comments, or code fences to the `.ris` file.
- In short: 该用中文报告的部分用中文；该保留英文/官方格式的稿件、文献元数据与 RIS 字段保持英文或原始格式。

---

## 0.25 MCP Readiness and Runtime Availability

Use this readiness gate before any workflow that depends on Zotero or PubMed. The static validator can only inspect this Markdown specification; it does not connect to Zotero, does not execute PubMed, and does not prove that runtime MCP tools are available in the active Agent IDE session.

### Dependency model

| Layer | Requirement | Runtime availability rule |
|-------|-------------|---------------------------|
| Zotero MCP | Required (`metadata.requires: zotero-mcp`) | The active session must expose callable Zotero tools before local library search, metadata inspection, PDF/notes access, or RIS generation from Zotero records. |
| PubMed MCP | Optional (`metadata.optional: pubmed-mcp`) | The active session must expose callable PubMed / NCBI-capable tools before PubMed expansion can be executed or reported as completed. |
| Static validation | Repository-side guardrail only | `scripts/validate-skill.py` checks structure, dependency metadata, templates, and safety text; it does not run a live MCP smoke test. |

### Runtime readiness checklist

1. **Zotero readiness**: confirm Zotero MCP tools are visible before claiming local-library search, semantic search, metadata retrieval, PDF links, annotations, or notes were inspected.
2. **PubMed readiness**: confirm the active session exposes a PubMed-capable callable tool before PubMed expansion. For PancrePal-style servers, expected tools include `pubmed_search`, `pubmed_get_details`, `pubmed_extract_info`, `pubmed_find_related`, `pubmed_detect_fulltext`, `pubmed_download_fulltext`, `pubmed_system_status`, and `pubmed_manage_cache`.
3. **Zotero is not PubMed**: do not treat Zotero MCP as a PubMed search client. Zotero records may contain DOI/PMID links, but live PubMed expansion requires a separate visible PubMed/NCBI-capable tool.
4. **No silent fallback**: if a required tool is unavailable, report the limitation and provide a copyable query or next step. Do not imply that unavailable tools were executed.

### PubMed status decision tree

Use these status values consistently in reports and final warnings:

| Condition | Required report status | RIS consequence |
|-----------|------------------------|-----------------|
| No PubMed-capable tool is visible in the active session | `⚠️ Tool unavailable; search not executed` | Do not create PubMed-only RIS records. Include the planned PubMed query for manual use. |
| PubMed tool is visible, but workflow is explicit chat-only or non-biomedical and PubMed was intentionally skipped | `Not executed` with reason | Do not create PubMed-only RIS records. |
| PubMed tool is visible, but the search call failed | `Failed; query reported` | Do not create PubMed-only RIS records. Report query/error briefly. |
| PubMed search actually ran and selected PMID metadata was inspected with `pubmed_get_details` or `pubmed_extract_info` | `Completed` | PubMed-only RIS records are allowed only for selected records with sufficient inspected metadata. |

Only actual PubMed execution plus inspected metadata can justify `Completed` or PubMed-only RIS inclusion. Tool visibility alone is not enough.

---

## 0.5 Library Health Check

Use when the user asks for Zotero library status or readiness, including phrases such as "库状态", "健康检查", "preflight", "索引状态", "library status", "health check", or "index status". This mode gives a read-only overview of whether the library is ready for semantic search, evidence review, citation verification, and paragraph analysis.

### Checks

| Check | Zotero MCP tool | What to report |
|-------|-----------------|----------------|
| Semantic index status | `zotero_get_search_database_status` | Indexed item count, full-text index coverage if available, last update time, and whether `zotero_update_search_database` is recommended |
| PDF coverage | `zotero_advanced_search` for total library items and items with attachments/PDFs | Number of items with PDF / total items, percentage, and whether full-text verification may be limited |
| Duplicate items | `zotero_find_duplicates` | Number of duplicate groups and whether manual merge review is recommended |
| Missing abstracts | `zotero_advanced_search` with empty abstract conditions | Number of items without abstracts and whether metadata enrichment is recommended |

### Process

1. Run the four checks above when the user asks for a health check.
2. Keep all actions read-only. Do not update the semantic index, merge duplicates, edit metadata, move items, or add/delete items during the health check.
3. If a check cannot be completed because a tool is unavailable, Zotero is not reachable, or a query is unsupported, mark that row as `⚠️` and explain the limitation. Do not estimate or invent counts for incomplete checks.
4. Recommend fixes, but ask for explicit confirmation before running any repair action such as `zotero_update_search_database`, duplicate merging, metadata editing, or batch tagging.

### Output Format

```markdown
## Zotero Library Health Check

| Check | Status | Result | Suggested action |
|-------|--------|--------|------------------|
| Semantic index | ✅ / ⚠️ / ❌ | Indexed: N items; last update: YYYY-MM-DD | No action / Run incremental update / Consider full rebuild only with confirmation |
| PDF coverage | ✅ / ⚠️ / ❌ | PDFs: N / total (X%) | Add PDFs for key missing items; update full-text index if needed |
| Duplicate items | ✅ / ⚠️ / ❌ | Duplicate groups: N | Review duplicates manually before merging |
| Missing abstracts | ✅ / ⚠️ / ❌ | Missing abstracts: N | Enrich metadata for high-priority items |

### Summary
- Overall readiness: ✅ good / ⚠️ usable with limitations / ❌ needs maintenance
- Safe next step: [one recommended read-only or confirmation-required action]
```

### Safety Rules

- Health check is read-only.
- Never merge duplicates, update tags, rebuild indexes, edit metadata, move collections, or delete items without explicit user confirmation.
- Prefer incremental semantic database updates over force rebuilds.
- If recommending repair actions, separate them from the health report and ask the user which action to run.

---

## Tool Selection

Choose the right Zotero MCP tool for each task:

- **Conceptual literature discovery** → `zotero_semantic_search` first.
- **Exact title, DOI, PMID, author, keyword** → `zotero_search_items` or `zotero_advanced_search`.
- **Citation-key lookup** → `zotero_search_by_citation_key`.
- **Metadata, abstracts, BibTeX/JSON export** → `zotero_get_item_metadata`; required before writing RIS records for Zotero items.
- **Attachments / PDF links** → `zotero_get_item_children` or `zotero_get_items_children` to find attachment keys for `zotero://open-pdf/library/items/{attachment_key}` links.
- **Full text** → `zotero_get_item_fulltext` or `zotero_read_pdf_pages`.
- **Annotations and reading notes** → `zotero_get_annotations` and `zotero_get_notes`.
- **Collection-level search** → `zotero_get_collections`, `zotero_search_collections`, `zotero_get_collection_items`.
- **Semantic database status** → `zotero_get_search_database_status`.
- **Semantic database update** → `zotero_update_search_database`. Only when needed; prefer incremental `update-db`.
- **RIS output** → generate from inspected Zotero metadata and verified PubMed metadata only; never infer missing bibliographic fields from memory.

When PubMed MCP tools are visible, use them as a separate biomedical evidence layer rather than a replacement for Zotero:

- **Broad PubMed expansion** → `pubmed_search` with Boolean terms, MeSH terms, filters, `sort_by`, and `format`; use `format="compact"` for scanning and `format="detailed"` for selected evidence.
- **Canonical PMID metadata** → `pubmed_get_details` for selected PMIDs before citing, deduplicating, or writing RIS records.
- **Targeted metadata extraction** → `pubmed_extract_info` for `basic_info`, `authors`, `abstract_summary`, `keywords`, or `doi_link` when a full record is unnecessary.
- **Citation-chaining / key-paper expansion** → `pubmed_find_related` with `type="similar"` or `type="reviews"` after identifying a key PMID.
- **OA full-text triage** → `pubmed_detect_fulltext` when `FULLTEXT_MODE=enabled` and the workflow needs full text beyond abstracts.
- **OA PDF download** → `pubmed_download_fulltext` only for OA articles, after checking availability; downloaded PDFs are external cache artifacts, not Zotero attachments unless the user later confirms import/attachment actions.
- **PubMed diagnostics** → `pubmed_system_status` and `pubmed_manage_cache` for troubleshooting; do not clear caches without explicit confirmation.
- **EndNote-compatible export** → if a PubMed tool/server directly offers RIS, NBIB, EndNote, BibTeX, or citation export in the active tool list, prefer that exporter for PubMed-only records; otherwise generate RIS from inspected `pubmed_get_details` metadata using the local RIS rules below.

## Safety Rules

Always ask for explicit confirmation before:

- deleting Zotero items, notes, or annotations;
- merging duplicate items;
- batch-updating tags;
- moving many items between collections;
- force-rebuilding the semantic database;
- adding many items at once;
- overwriting notes or annotation comments.

Never fabricate citations, titles, authors, years, journal names, DOI, PMID, Zotero item keys, or RIS records.
If no relevant source is found in Zotero, say so clearly and suggest an external search query instead.

---

## 1. Semantic + Structured Search

### Process

1. If the user asks in natural language, first expand their query into structured search terms.
2. Run **semantic search** first (concept matching, finds conceptually related papers even without keyword overlap).
3. If results are insufficient, fall back to **keyword search** with relevant filters (tags, authors, year range, item type).
4. Present results with the standardized format below.

### Query Expansion Examples

| User says | Expanded structured query |
|-----------|--------------------------|
| "气候变化 心血管疾病 风险" | `q: "climate change cardiovascular disease risk", semantic: true, tags: ["cardiovascular"], year: 2020-2026` |
| "孟德尔随机化 药物靶点 2型糖尿病" | `q: "Mendelian randomization drug targets type 2 diabetes", semantic: true, tags: ["MR", "drug targets"], itemType: "journalArticle"` |
| "肠道菌群 抑郁症 机制" | `q: "gut microbiota depression mechanism", semantic: true, year: 2020-2026` |

### Standardized Output Format

Present **all** hits in a single scannable table — one row per paper. Do **not** emit a nested bullet block per paper.

```markdown
| # | Citation (Author Year) | Type | Role | Key | Sim. | Why relevant |
|---|------------------------|------|------|-----|------|--------------|
| 1 | Wang 2022 | semantic | method | Y2FFFQSB | 0.84 | LST/sedentary GWAS; 99 loci |
```

- **Type** = semantic / keyword / tag / collection.
- **Role** = background / mechanism / clinical / method / limitation.
- **Sim.** = similarity score, or "—" for keyword/tag hits.
- **Why relevant** = one short clause, not a sentence list.

Then add a compact **Refs** appendix so full metadata appears exactly once (and only here). Output format: see **Appendix: Output Templates → REFS_BLOCK**.

After the table + Refs, refer to papers only as `Author Year (KEY)` — never re-list title/journal/DOI again.

---

## 1.5 Collection and Tag Search

Use collection or tag filters when:

- the user names a specific research project;
- the user asks for papers from a known Zotero folder or collection;
- the query is broad and the user's library is large;
- the user asks for reviewed, important, included, excluded, or to-read items;
- the user references systematic-review screening status, dissertation chapters, project folders, or reading-list tags.

### Suggested Workflow

1. **Detect structure hints**
   - Treat project names, folder names, collection names, and tag-like labels as possible Zotero structure filters.
   - Common tag hints include `reviewed`, `important`, `included`, `excluded`, `to-read`, `待读`, `已纳入`, `排除`, `重点`, and project-specific tags.
2. **Search collections by name**
   - Use `zotero_search_collections` when the user names a folder/project.
   - If several collections match, show a short numbered list and ask the user to choose.
3. **Retrieve collection items**
   - Use `zotero_get_collection_items` for the selected collection.
   - Use `detail: "summary"` for overview and `detail: "keys_only"` when the collection is large and a follow-up search is needed.
4. **Search within the collection if needed**
   - Use `zotero_search_items` with `collection_key` when keyword/metadata filtering is enough.
   - Use semantic search for conceptual relevance, then intersect or annotate results with collection membership when exact collection-scoped semantic search is unavailable.
5. **Apply tag filters**
   - Use `zotero_search_by_tag` for explicit tag requests.
   - Combine tag filters with query terms when the user asks for status-specific literature, e.g. included studies about an outcome.
6. **Combine relevance with structure**
   - Rank by semantic/keyword relevance, but clearly mark collection and tag membership.
   - Prefer papers inside the named collection/tag when the user explicitly scopes the request.

### Output Notes

- In search result tables, use `Type = collection` or `tag` when the hit is included because of Zotero organization.
- Add collection/tag context in `Why relevant`, e.g. `in PCOS-review collection; tagged included`.
- Do not move items between collections or batch-update tags without explicit user confirmation.

---

## 2. Paragraph Evidence & Citation Analysis

Use when the user pastes a manuscript paragraph, draft passage, or multi-sentence text and asks for evidence, citation support, writing suggestions, or citation insertion. This module replaces the former separate evidence-chain and writing-suggestion modes.

### Core Principle

Run **one Zotero search pass** for the paragraph, then produce **two output layers** from the same result set:

- **Layer A: evidence quality** — each extracted claim receives a standardized evidence level, support strength, source boundary, and gap status.
- **Layer B: citation recommendation** — each sentence receives recommended citations and a concise citation rationale.

### Source Layer: Current-study Finding vs External Evidence

Assign every extracted claim exactly one `Source layer` before interpreting evidence. This boundary prevents the workflow from using external literature to incorrectly "prove" the user's current-study findings.

| Source layer | Definition | Required wording pattern |
|--------------|------------|--------------------------|
| `Current study` | A result, observation, statistic, model output, table/figure result, or interpretation supplied by the user or produced in the current manuscript/analysis. | `In our analysis...`, `The present study identified...`, `Our findings suggest...`, `本研究发现...` |
| `Zotero external evidence` | Evidence from inspected Zotero library records, including metadata, abstracts, notes, annotations, or full text. | `Previous studies show...`, `Published evidence supports...`, `Zotero-indexed literature reports...` |
| `PubMed external evidence` | Evidence from PubMed expansion records after a completed PubMed search and inspected PMID metadata. | `PubMed-indexed studies report...`, `Published evidence from PubMed supports...` |
| `Interpretive bridge` | A cautious inference connecting current-study findings to external evidence, mechanism, or plausibility. | `These findings are consistent with...`, `may suggest...`, `provide biological plausibility for...` |
| `Unsupported gap` | A claim for which no adequate direct, indirect, mechanistic, or verified evidence was retrieved. | `requires validation`, `was not directly supported by retrieved evidence`, `needs verification` |

Claims that must normally be marked `Current study` unless the user explicitly states they are from an external cited source:

- SMR, MR, TWAS, GWAS, colocalization, fine-mapping, LDSC, MAGMA, PRS, genetic correlation, QTL or eQTL/pQTL integration;
- pathway enrichment, gene-set enrichment, cell-type enrichment, cell enrichment, tissue enrichment, network analysis, module detection;
- candidate gene prioritization, drug-target prioritization, target ranking, causal-gene nomination;
- differential expression, single-cell analysis, spatial transcriptomics, omics integration, mediation analysis;
- cohort, clinical, statistical-model, sensitivity-analysis, subgroup-analysis, or figure/table results supplied by the user;
- manuscript wording such as `we found`, `our analysis identified`, `the present study shows`, `本研究发现`, `我们的结果提示`, or equivalent.

External literature can support background, prior association, method, mechanism, or biological plausibility. It must not be described as proving, confirming, validating, or replicating a current-study finding unless the retrieved external source directly tests the same claim with a comparable design, exposure, outcome, population, and direction.

Required interpretation rules:

- If a claim is `Current study`, assign evidence level `D` unless an inspected comparable external replication supports the same finding.
- If external evidence only provides mechanism or background for a current-study claim, use `Interpretive bridge` wording and evidence level `C` or `D`, not `A`.
- If no direct or plausible evidence is found, mark `Source layer = Unsupported gap` and evidence level `E`.
- The Claim–Evidence Matrix must include both `Source layer` and `Evidence level` so readers can see whether a statement is current-study output, external evidence, a bridge inference, or a gap.

Recommended wording:

- Current study: `In our analysis...`, `The present study identified...`, `Our findings suggest...`.
- External evidence: `Previous studies show...`, `Published evidence supports...`, `Prior literature reports...`.
- Interpretive bridge: `These findings are consistent with...`, `may suggest...`, `provide biological plausibility for...`.
- Unsupported gap: `requires validation`, `was not directly supported by retrieved evidence`, `should be verified before use`.

Forbidden wording unless directly supported by comparable external evidence:

- `Previous studies confirmed our SMR/TWAS/MR result`.
- `Published literature proves our candidate gene prioritization`.
- `External evidence validates our enrichment result`.
- `This citation demonstrates that our current-study association is causal`.
- `The retrieved papers confirm the current study's BMI-independent or pleiotropy result`.

### Unified Evidence Level

Assign every extracted claim exactly one evidence level from `A` to `E`. Use the same level in chat output, Markdown evidence reports, reviewer-risk assessment, and manuscript wording recommendations so evidence strength does not drift across reports.

| Level | Name | Definition | Judgment criteria | Recommended wording | Avoid |
|-------|------|------------|-------------------|---------------------|-------|
| `A` | Exact direct support | External literature directly supports the exact claim. | The retrieved source matches the claim's exposure/intervention, outcome, direction, population/context, and study-design implication closely enough to support the sentence as written. | `supported`, `directly supported`, `reported`, `shown to be associated with` when the source design supports that wording | Adding causal, population, subgroup, or independence claims not present in the source |
| `B` | Close direct support | External literature directly supports a closely related claim, but not the exact manuscript claim. | At least one key element differs, such as phenotype, population, exposure definition, mechanism detail, time scale, or study design. | `consistent with`, `supports a related claim`, `aligns with evidence that...` | `proves`, `confirms`, or wording that treats the related source as exact support |
| `C` | Plausibility support | Evidence is mechanistic, background, review-based, pathway-level, methodological, or otherwise indirect. | The source supports biological plausibility, context, mechanism, terminology, or method, but does not directly test the full claim. | `biologically plausible`, `may align with`, `may contribute to`, `provides mechanistic context` | Treating mechanism or background as direct empirical support |
| `D` | Current-study only | The claim is primarily a finding from the user's current study; external literature can only provide context or plausibility unless direct replication is retrieved. | The claim comes from the user's data, analysis, tables, figures, or wording such as `our analysis`, `we found`, `本研究发现`, or `the present study identified`. | `in our analysis`, `our findings suggest`, `the present study identified`, `consistent with prior evidence` | `previous studies confirmed our finding` unless a comparable external replication was inspected |
| `E` | Unsupported / contradicted / verify | The claim is unsupported, contradicted, unverifiable with available sources, or requires citation/metadata verification. | No adequate evidence was found; retrieved evidence conflicts with the claim; or a key citation, concept, DOI/PMID, title, or metadata field remains unverified. | `remove`, `verify`, `hedge strongly`, `requires validation`, `not directly supported by retrieved evidence` | Presenting the claim as established fact |

Evidence-level rules:

- `D` explicitly means `current-study only`. Do not use external mechanistic or background literature as direct proof of the user's own SMR, MR, TWAS, GWAS, enrichment, candidate-gene, cohort, or statistical finding.
- `C` cannot be upgraded to `A` or `B` unless direct empirical evidence for the same claim is retrieved and inspected.
- `E` claims must not appear in manuscript-ready text as confident factual statements; remove, verify, convert to a knowledge gap, or hedge strongly.
- Recommended Manuscript Text must follow the level: A/B can use moderate confidence, C/D require cautious or bridge wording, and E requires removal, verification, or strong hedging.

Do not repeatedly search Zotero for each output layer. Do not ask the user to choose between "find evidence" and "add citations" modes.

When the request is a citation-support or export request, this module is the analysis stage of the **Paragraph Citation Package Workflow (Module 2 + Module 2.5)**. In that full workflow, the agent must continue to Module 2.5 after the Zotero local search and paragraph analysis; PubMed expansion is attempted automatically after Zotero local search when a PubMed-capable tool is configured and visible. Chat-only use of Module 2 requires an explicit opt-out such as `不要生成文件` or `只在聊天输出`.

### Process

1. **Sentence splitting + claim extraction**
   - Split the paragraph into sentences.
   - Extract 1-2 core factual/conceptual claims per sentence.
   - Preserve sentence order so claim IDs can be mapped back to citation placement.
2. **Batch query construction + one search pass**
   - Combine all claims into a compact batch of search queries.
   - Run `zotero_semantic_search` first for conceptual matching.
   - If coverage is insufficient, run one keyword/structured fallback with `zotero_search_items` or `zotero_advanced_search` using the same claim set.
   - Deduplicate results and build one reusable candidate evidence pool.
3. **Two-layer analysis from the same evidence pool**
   - **Layer A: Claim-evidence matrix** — map each claim to the best available citation(s), assign exactly one source layer and one A-E evidence level, record support strength, and mark gap status.
   - **Layer B: Sentence-level citation recommendations** — map each sentence to the citation(s) that should be inserted, carry forward the same source layer and A-E evidence level, and explain why.
   - Do not use a different strength label or source boundary in Layer B than the level assigned in Layer A. If sentence-level wording combines multiple claims, use the most conservative evidence level and explicitly separate current-study wording from external-evidence wording.
4. **Diff paragraph**
   - Provide a revised paragraph showing citation insertions and necessary wording changes.
   - Mark deletions with `~~strikethrough~~` and additions with `**bold**`.
   - Keep unchanged text unmarked so the user can see exactly what changed.
   - End with a change summary in this format: `改动：+N词/-M词，修改原因：[简短说明]`.
5. **Gap summary + package/external handoff**
   - Summarize claims with no adequate Zotero evidence.
   - For chat-only Module 2 output, propose external search queries for each gap and ask whether to start external search using **External Source Fallback**.
   - For the full **Paragraph Citation Package Workflow**, do not stop at the gap prompt: continue to Module 2.5, where automatic PubMed expansion is attempted after Zotero local search when a PubMed-capable tool is configured and visible.
   - If no PubMed-capable tool is available in package mode, include the copyable PubMed query and status `⚠️ Tool unavailable; search not executed` in the Markdown report instead of implying PubMed was searched.

### Evidence and Rationale Labels

Use the unified evidence level above as the primary strength label for every claim. The labels below describe the evidence type or citation role and should be used alongside the A-E level inside the tables, especially in the "Strength", "Evidence level", and "Citation rationale" columns:

- **Direct evidence**: directly supports the claim.
- **Indirect evidence**: supports part of the mechanism, context, or related association.
- **Mechanistic evidence**: explains a biological, behavioral, theoretical, or methodological mechanism.
- **Methodological evidence**: supports the design, measurement, or analytical method.
- **Background/context**: useful for introduction, framing, or terminology.
- **Contrasting evidence**: reports inconsistent or opposite findings; use to hedge or qualify wording.
- **Replace citation**: a library source is more recent, more specific, or better aligned than an existing citation.
- **Terminology alignment**: Zotero sources consistently use a different term or construct.
- **Gap**: no adequate Zotero evidence found.

The former writing-suggestion categories are not shown as a standalone section; fold them into the sentence-level "Citation rationale" column.

### Output Format

Always use this **table-first, no-repetition** layout. Full metadata appears once in the `Refs` block; everywhere else cite sources as `Author Year (KEY)`.

Use this structure:

```markdown
## 段落分析：<主题短语>

### Refs（元数据唯一出现一次）
输出格式见 **Appendix: Output Templates → REFS_BLOCK**。

### 层A：主张-证据矩阵
输出格式见 **Appendix: Output Templates → CLAIM_EVIDENCE_MATRIX**。

### 层B：逐句引文推荐
输出格式见 **Appendix: Output Templates → WRITING_SUGGESTIONS_TABLE**。

### 修改版段落（diff）
输出格式见 **Appendix: Output Templates → DIFF_REVISED_PARAGRAPH**。

### Gap 与外部搜索
- ⚠️ 主张2 无库内证据 → 建议查询：`"Z causes W" mechanism`
- 是否启动外部搜索？(y/n)
```

### Gap Handling

When any row in the Layer A claim-evidence matrix has `Gap? = ⚠️ 是`, handle the gap according to workflow mode.

- **Full Paragraph Citation Package Workflow**: continue to Module 2.5 automatically. PubMed expansion is the built-in biomedical expansion step after Zotero local search when a PubMed-capable tool is configured and visible; if unavailable, report the query and `⚠️ Tool unavailable; search not executed`.
- **Chat-only Module 2**: enter the interactive gap-handling flow below after presenting the paragraph analysis. Do not run external searches unless the user confirms.

Interactive chat-only flow:

1. **Count gap claims**
   - Report the number of unsupported or insufficiently supported claims.
   - Preserve claim IDs from Layer A so the user can trace each gap back to the paragraph.
2. **Construct bilingual external queries**
   - For each gap, generate an English `query` and a Chinese `query_zh` when the paragraph or user request is Chinese.
   - Prefer standard biomedical terminology and MeSH terms when applicable.
   - Keep queries specific enough to retrieve direct evidence, e.g. exposure/intervention + outcome + mechanism/study type.
3. **Ask before external search**
   - Show a compact gap summary and ask: `发现 N 处证据缺口，是否启动外部文献搜索？(y/n)`
   - If the user says yes, follow **External Source Fallback**.
   - Use external MCP tools such as Crossref/OpenAlex/Semantic Scholar or paper-search/PubMed only when those tools are configured and visible in the current environment. If they are unavailable, provide ready-to-copy external search queries instead of implying that the search was executed.
4. **Return top external candidates**
   - For each gap, return up to top-3 external results.
   - Mark every result as external and include source, title, authors, year, DOI/URL, and why it may fill the gap.
   - Do not treat external results as library evidence until added to Zotero and inspected.
5. **Ask before adding to Zotero**
   - After external results are shown, ask whether to add selected items to Zotero using `zotero_add_by_doi` or `zotero_add_by_url`.
   - Adding items requires explicit user confirmation.
   - Support collection placement in the confirmation prompt:
     - **指定分类**: ask the user for the target collection name/key, then pass it via the `collections` parameter.
     - **当前分类**: if the current working context includes a collection key, offer to add to that collection automatically; confirm the collection name/key before adding.
     - **未指定分类**: add to the main library only after confirmation.

Use this output shape:

```markdown
### Gap Handling
- 发现 2 处证据缺口。

| Gap claim | query | query_zh | Suggested external source |
|-----------|-------|----------|---------------------------|
| #2 Z导致W | `Z causes W mechanism MeSH_term` | `Z 导致 W 机制` | PubMed / Semantic Scholar |

是否启动外部文献搜索？(y/n)

<!-- If yes, after external search: -->
### External candidates
| Gap | External result | Source | DOI/URL | Why relevant |
|-----|-----------------|--------|---------|--------------|
| #2 | Author 2024 | PubMed | 10.xxxx/xxxx | Directly tests Z→W |

是否将以上结果添加到 Zotero？请选择：
1. 添加到当前分类：<collection name/key>
2. 添加到指定分类（请提供分类名/key）
3. 只添加到主库
4. 不添加
```

### Rules

- Keep the paragraph's original language unless the user asks for translation.
- Prefer 3-7 high-value citations over exhaustive citation stuffing.
- If evidence is indirect, mixed, observational, or mechanistic only, assign evidence level C unless a more specific rule requires D or E, and recommend hedging language rather than causal wording.
- Carry evidence levels into writing suggestions: A/B may support moderately confident citation placement, C/D require bridge or hedge wording, and E should be removed, verified, or reframed as a gap.
- Separate current-study findings from external evidence in manuscript wording: write current results as `In our analysis...` or `The present study identified...`, then use external citations only as `Previous studies show...` or `These findings are consistent with...` bridge support.
- Use the same Zotero result pool for both Layer A and Layer B; only search again if the user explicitly requests deeper follow-up.
- Do not fabricate missing support. Mark gaps clearly. In chat-only mode, hand off to external search only after asking; in the full Paragraph Citation Package Workflow, continue to Module 2.5 and report PubMed expansion status honestly.

---

## 2.5 Evidence Package Export

Use when the user asks to save results, generate an evidence package, export EndNote references, or produce durable files after a search or paragraph evidence review. For paragraph citation-support requests, this module is the export stage of the unified **Paragraph Citation Package Workflow (Module 2 + Module 2.5)**: **Module 2 → Module 2.5** means analysis first, then export.

Visible default pipeline for paragraph citation/export work:

```text
paragraph → claim extraction → one Zotero local search pass → evidence matrix → citation placement → revised/diff paragraph → Zotero metadata + PDF links → automatic PubMed expansion as a second evidence source when available → combined evidence synthesis and deduplication → reference export standardization by PMID/DOI → metadata QC → Markdown evidence report → EndNote RIS
```

The default deliverable is exactly two files inside a skill-named, topic-specific output folder:

```text
zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_evidence_review.md
zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_references.ris
```

Do not create extra JSON, BibTeX, EndNote XML, DOI lists, or log files unless the user explicitly requests them. The Markdown report is the human-readable evidence workspace; the RIS file is the EndNote import file.

### Trigger Conditions

Route to this module when the user asks for any of the following:

- `/zotero-evidence-review` plus a short request to find evidence, add citations, export a report, or create reusable writing outputs; this simple-request entry defaults to the complete workflow unless there is an explicit chat-only opt-out.
- `Evidence Package`, `Markdown report`, `EndNote`, `RIS`, `保存报告`, `导出参考文献`, `生成文件`, or `输出文件`.
- Default citation-support workflow triggers: `使用技能`, `完整工作流`, `找引文`, `补引用`, `推荐引用`, `citation`, `refs`, `reference`, `参考文献`, or `文献引用` when attached to a paragraph, manuscript passage, or literature-search request.
- A paragraph evidence review plus a request to save or export results.
- A literature search where the user wants a reusable report rather than chat-only results.

Do not route to this module when the user explicitly opts out with `只在聊天输出`, `不要生成文件`, `不导出`, `chat only`, or equivalent.

### Workflow

1. **Run or reuse the evidence workflow**
   - For paragraph input, run **Module 2** first as the analysis stage of the **Paragraph Citation Package Workflow (Module 2 + Module 2.5)**.
   - For paragraph citation-support requests such as `/zotero-evidence-review`, `使用技能`, `找证据`, `找引文`, `补引用`, `推荐引用`, `citation`, `refs`, `参考文献`, or `文献引用`, default to the full workflow and write both `zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_evidence_review.md` and `zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_references.ris` unless the user explicitly opts out of file generation.
   - For topic/search input, run **Module 1** first and convert the final included papers into a reference table.
   - For biomedical paragraph/search requests, the package workflow attempts automatic PubMed expansion after Zotero local search when a PubMed-capable tool is configured and visible.
   - Other external source fallback beyond this built-in PubMed expansion still follows **Module 5: External Source Fallback** and requires availability checks and user confirmation where specified.
2. **Collect canonical metadata**
   - For every Zotero item considered for the final report or RIS, retrieve metadata with `zotero_get_item_metadata`.
   - Retrieve child attachments with `zotero_get_item_children` or `zotero_get_items_children` when PDF links are needed.
   - Use Zotero metadata as the authority for Zotero items. Do not fill missing authors, titles, journals, pages, DOI, PMID, or years from memory.
3. **Run automatic PubMed expansion as a second evidence source when available**
   - After Zotero local search, construct a PubMed query from the topic, extracted claims, and core biomedical concepts.
   - Execute PubMed search automatically in the full package workflow only if a PubMed-capable tool is configured and visible in the current MCP tool list.
   - Treat a PubMed-capable tool as visible only when the active session exposes a callable tool whose name or description clearly indicates PubMed / NCBI E-utilities search, such as `pubmed`, `simple-pubmed`, `pubmed-data-server`, `ncbi`, `esearch`, `efetch`, `search-pubmed`, `get_paper_fulltext`, or equivalent biomedical database search capability.
   - Do not assume Zotero MCP itself can search PubMed. Zotero MCP may contain Zotero records with PMID links, but PubMed expansion requires a separate visible PubMed/NCBI-capable tool.
   - Treat Zotero and PubMed as two evidence-source steps: Zotero local evidence first, then PubMed expansion for additional or confirming evidence.
   - For PancrePal PubMed MCP, use `pubmed_search` first, then call `pubmed_get_details` for PMIDs that may enter the report/RIS; use `pubmed_extract_info` for targeted DOI/authors/abstract extraction when token efficiency matters.
   - For one or two highly relevant PMIDs, use `pubmed_find_related` with `type="reviews"` or `type="similar"` when the user asks for comprehensive coverage, review evidence, or adjacent mechanisms.
   - If full-text support is needed and full-text tools are visible, use `pubmed_detect_fulltext` before any OA PDF download; do not treat downloaded PubMed PDFs as Zotero-local evidence unless the user explicitly imports or attaches them.
   - If no PubMed-capable tool is available, include the copyable PubMed query in the report and mark PubMed expansion as `⚠️ Tool unavailable; search not executed`.
   - If a PubMed-capable tool is visible but the search fails, mark PubMed expansion as `Failed; query reported`, report the attempted query/error briefly, and do not create PubMed-only RIS records.
4. **Combine Zotero and PubMed evidence results**
   - Build a combined candidate table containing Zotero records and PubMed expansion records.
   - Deduplicate evidence candidates by DOI first, then PMID, normalized title, then fuzzy first-author + year + journal.
   - Preserve source labels separately from export metadata: `Zotero`, `PubMed`, or `Zotero + PubMed`.
   - When the same article appears in both Zotero and PubMed, mark source as `Zotero + PubMed` and retain Zotero item/PDF/collection links in the report.
   - When a PubMed record is not present in Zotero and is relevant, mark source as `PubMed` and recommendation as `consider importing` or `recommend citing`.
   - If DOI/PMID/title conflicts suggest two records may not be the same article, mark `Possible metadata mismatch` and keep them unresolved until checked.
5. **Standardize RIS references at export time by PMID/DOI**
   - After selecting final recommended references, standardize the RIS metadata using identifiers rather than relying only on local Zotero fields.
   - If a selected reference has a PMID and PubMed metadata can be retrieved, use the PMID/PubMed record as the preferred source for RIS citation fields.
   - If no PMID is available but a DOI is available and DOI metadata can be retrieved, use DOI metadata as the preferred source for RIS citation fields.
   - If neither PMID nor DOI metadata is available, use inspected Zotero metadata for Zotero records or inspected PubMed metadata for PubMed records.
   - Keep Zotero source labels and links in the Markdown report, but use the standardized PMID/DOI-derived metadata for the EndNote RIS when available.
   - Never silently standardize: report each selected reference's `Evidence source` and `RIS standardization source` in the Markdown QC table.
6. **Run metadata quality control**
   - Check missing metadata before RIS export: DOI, PMID, journal / publication title, year, volume, issue, pages, and authors.
   - Check Zotero-vs-PubMed and identifier-derived metadata conflicts for DOI, PMID, normalized title, publication year, and journal.
   - Check possible duplicate records by DOI, PMID, normalized title, and fuzzy author + year + journal.
   - Report missing metadata, metadata mismatch, and duplicate warning rows in the Markdown report.
   - Exclude unresolved metadata conflicts from RIS by default; do not silently write questionable records.
7. **Select RIS references**
   - Include final recommended Zotero citations.
   - Include PubMed-only papers only when they are marked `recommend citing` or `consider importing`, and only when PubMed metadata is sufficient and comes from an actually completed PubMed search.
   - Exclude low-relevance hits, duplicate records, and unresolved metadata conflicts by default.
8. **Run pre-write QA self-check, then write the two files**
   - Before writing Markdown or RIS content to disk, run the internal **Evidence Package QA Self-Check Prompt** against the complete draft report, planned RIS records, PubMed execution log, metadata QC table, and intended output paths.
   - If the self-check finds missing status, missing critical warnings, missing copy-ready text, missing claim evidence level/source layer, current-study/external-evidence confusion, inaccurate PubMed status, invalid RIS content, absolute paths, unresolved metadata mismatch, or overconfident E-level wording, revise the draft report/RIS first and repeat the self-check.
   - Create or reuse the package output directory according to **Default Output Directory** only after the draft passes the pre-write self-check.
   - Save the Markdown report with the `EVIDENCE_REVIEW_REPORT` template.
   - Save the RIS file with the `RIS_REFERENCE_FILE` template and rules.
   - Run the post-write QA gate before announcing completion: confirm the written Markdown/RIS still match the same checks, and that final chat exposes only status, relative paths, and critical warnings.
   - Final chat output must use this exact compact structure and include no internal checklist details:

```markdown
Generated Evidence Package:
- Status: {Ready / Caution / Partial / Superseded / Unknown}
- Markdown report: `zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_evidence_review.md`
- EndNote RIS: `zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_references.ris`

Critical Warnings:
- {warning or No critical warnings}
```

### Default Output Directory

By default, write evidence packages under a deterministic skill output root, then a topic-and-timestamp run folder. Do not write evidence package files into the repository/project root.

```text
zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/
```

The fixed `zotero-evidence-output/` root identifies the files as this skill's output. The run folder combines an LLM-generated brief topic slug with a current local date-time suffix, so repeated runs for the same topic remain easy to sort and unlikely to collide.

The folder must contain only the default two deliverables unless the user explicitly requests additional files:

```text
zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_evidence_review.md
zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_references.ris
```

If the selected run folder already exists, create `zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_v2/`, `zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_v3/`, etc. Do not overwrite an existing evidence package unless the user explicitly confirms replacement.

### Default Naming

Use an **LLM-generated brief topic slug** plus a current local date-time suffix. The brief topic slug must be inferred from the user's paragraph, claim, or search question; the user should not need to provide it manually.

Naming components:

- `brief_topic_slug`: a short, specific summary of the topic, usually 2-6 words.
- `YYYY-MM-DD_HHMMSS`: current local date and time to seconds, e.g. `2026-06-18_143512`.
- Markdown suffix: `_evidence_review.md`.
- RIS suffix: `_references.ris`.

Slug rules:

- Use lowercase ASCII words when possible.
- Convert spaces, punctuation, slashes, and repeated separators to single underscores.
- Keep meaningful domain abbreviations such as `pcos`, `mr`, `gwas`, or `il6`.
- Keep the slug short but descriptive, usually 2-6 words, e.g. `sedentary_behavior_pcos`.
- Do not use generic literals such as `topic`, `review`, `references`, `output`, `results`, or `zotero` alone.

Default package paths:

```text
zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_evidence_review.md
zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_references.ris
```

If files already exist inside the selected folder, append `_v2`, `_v3`, etc. to the run folder or filenames. Do not overwrite an existing evidence package unless the user explicitly confirms replacement.

### Run Relationship and Superseded Mechanism

Evidence package runs can be related when the user revisits the same topic, expands a previous search, or generates evidence for a different manuscript section using overlapping literature. The skill must record relationships in the new report without silently rewriting old reports.

Run relationship rules:

- Do not automatically modify old evidence package files. Only update, mark, or rewrite prior reports when the user explicitly asks to organize, summarize, consolidate, or supersede existing outputs.
- When a new evidence package is highly similar to existing packages, the new report metadata may list `Related prior packages` with paths, dates, topic slugs, and short relationship notes.
- Similarity judgment should use topic slug similarity, core keyword overlap, user-provided topic/paragraph overlap, selected references overlap, DOI/PMID overlap, and shared claim/manuscript-section context.
- If the new report is broader, newer, more complete, or has stronger search reproducibility / metadata QC than a prior package on the same claim scope, write `Potentially supersedes` in the new report.
- If the new report supports a different manuscript section, sub-claim, method/background/mechanism layer, or a narrower adjacent topic, write `Complementary to` rather than superseding.
- If relationship is uncertain, write `Related; supersession unclear` and explain the missing comparison information.
- `Superseded` package status must be assigned only when the report itself is explicitly being marked as replaced or when the user asks to manage prior outputs. A new report can say it `Potentially supersedes` an older report without changing the old report's status.
- Generate a project-level summary only when the user asks to整理/总结已有输出, consolidate runs, compare packages, or create a project overview. Do not create project-level summary files during ordinary evidence package generation.

Required metadata structure:

```markdown
| Related prior packages | {none / path + date + topic slug + relationship: Potentially supersedes / Complementary to / Related; supersession unclear} |
| Run relationship rationale | {topic slug similarity; core keyword overlap; selected references overlap; DOI/PMID overlap; manuscript section relationship} |
```

### Evidence Package Status

Every generated evidence package must receive exactly one status: `Ready`, `Caution`, `Partial`, `Superseded`, or `Unknown`. The status tells the user whether the package can be used for manuscript writing and what level of caution is required.

| Status | Definition | Trigger conditions | User guidance |
|--------|------------|-------------------|---------------|
| `Ready` | Searches completed as planned, central claims have direct or close support, metadata QC has no unresolved high-risk issue, and selected RIS records passed inspection. | All required evidence was inspected; PubMed is `Completed` when required for a biomedical topic or explicitly not required; central claims are mostly A/B; no unresolved metadata mismatch; no key citation/concept is unverified. | Can be used for drafting with normal scholarly caution. |
| `Caution` | The package is usable but has important caveats. | No direct evidence for a central claim; central evidence is mostly C/D; PubMed unavailable but not essential; duplicate records were detected and safely excluded or resolved; causal, BMI-independent, or pleiotropy wording requires hedge wording. | Use hedge wording and review warnings before manuscript use. |
| `Partial` | A required evidence layer or citation/metadata check is incomplete. | PubMed query failed when PubMed evidence is required; a key citation, PMIDs/DOIs, PMOS, or concept remains unverified; unresolved metadata mismatch affects selected references; PubMed-only evidence was planned but cannot be inspected; RIS cannot safely include a key record. | Do not treat as final; complete verification before submission. |
| `Superseded` | A later evidence package or updated run replaces this package. | The report explicitly identifies a newer package as replacing this one. Do not mark old files superseded automatically unless the user asks to manage prior outputs. | Keep for history only; use the newer package. |
| `Unknown` | The available workflow state is insufficient to determine status. | Tool results, search execution, metadata QC, or claim-level evidence status are unclear or unavailable. | Manual review required. |

Downgrade rules:

- `PubMed query failed` → at least `Partial` when PubMed evidence is required for a central biomedical claim; otherwise at least `Caution`.
- `PMOS`, key concept, citation, DOI/PMID, or title not verified → `Partial` for central claims, otherwise `Caution`.
- `No direct evidence for central claim` → at least `Caution`.
- `Metadata mismatch unresolved` → `Partial`, and the affected reference must be excluded from RIS.
- `Duplicate unresolved but excluded safely` → `Caution`.
- `All required evidence inspected and risks low` → `Ready`.
- If multiple triggers apply, use the most conservative status.

Status must appear in the Markdown report metadata, in the export-file section, and in the final chat summary after files are written.

### Critical Warnings

Critical warnings are the front-loaded reviewer-risk controls for problems that could mislead manuscript writing, citation use, or final submission. They must appear immediately after `Metadata and Use Status` and before `## 3. 核心结论（Bottom Line）` in every `EVIDENCE_REVIEW_REPORT`.

A case must be added to `Critical Warnings` when any of the following conditions applies:

- PubMed tool unavailable or PubMed query failed when PubMed is relevant to the biomedical evidence package.
- A central claim has no direct evidence.
- External evidence contradicts the draft claim.
- A central citation, concept, DOI/PMID, terminology, abbreviation, or claim remains unverified.
- Metadata mismatch remains unresolved for any candidate or selected reference.
- Duplicate Zotero records affect selected references or could change the canonical citation/RIS record.
- A current-study finding could be mistaken for external evidence support.
- Causal wording is not directly supported.
- BMI-independent wording is not directly supported.
- Horizontal pleiotropy wording is not directly supported.

Critical warning rules:

- Each warning must contain `Affected claim`, `Risk`, and `Required action`.
- The warning must be specific enough for the user to locate and revise the affected claim or citation.
- Critical warnings must be consistent with package `Status`; unresolved high-risk warnings usually require `Caution`, `Partial`, or `Unknown`, not `Ready`.
- Critical warnings must not be hidden only in later reviewer-risk or metadata-QC sections.
- If no critical warnings apply, write exactly: `No critical warnings`.
- Critical warnings may be referenced in `Annotated Recommended Text`, reviewer-risk assessment, metadata QC, and final chat summary, but they must not be inserted into `Copy-ready Manuscript Text`.
- The final chat summary must always display `Status` and `Critical warnings`; if none apply, write `No critical warnings`.

Required output structure:

```markdown
## Critical Warnings
| Affected claim | Risk | Required action |
|----------------|------|-----------------|
| ... | PubMed unavailable / no direct evidence / contradiction / unverified citation or concept / metadata mismatch / duplicate record / current-study vs external-evidence confusion / unsupported causal wording / unsupported BMI-independent claim / unsupported horizontal pleiotropy claim | Revise wording / verify citation / remove claim / complete PubMed search / resolve metadata / deduplicate records / mark as current-study only |
```

If there are no warnings:

```markdown
## Critical Warnings
No critical warnings
```

### Search Reproducibility

Every evidence package must include a reproducible search log so the Zotero and PubMed search process can be audited, repeated, or completed later. The section must cover Zotero semantic search, Zotero keyword search, and PubMed search even when one source returns no hits or cannot be executed.

Search reproducibility rules:

- Record every Zotero semantic query, Zotero keyword query, Zotero keyword/structured query, PubMed query, PubMed max results, and PubMed status used or planned.
- Each row must include `Source`, `Query`, `Mode`, `Max results`, `Status`, `Included`, and `Notes`.
- `Mode` must distinguish at least `semantic`, `keyword`, `structured`, `PubMed`, `PMID details`, `related`, or `full-text inspection` when applicable.
- `Max results` must record the requested limit/max_results for each search; if not available, write `Not recorded`, not a guessed number.
- `Status` must use explicit values such as `Completed`, `Not executed`, `⚠️ Tool unavailable; search not executed`, `Failed; query reported`, `No hits`, or `Partial`.
- PubMed failed or unavailable cases must still record the attempted or planned PubMed query and the failure reason.
- `Included` must record the included_count for that search row; for PubMed rows, list included PMIDs in `Notes` when available.
- `Notes` must record excluded records and reasons, failed reason, included PMIDs, duplicate/metadata exclusion notes, and whether full text was inspected.
- `full_text_inspected` must be marked as exactly `yes`, `no`, or `partial` in `Notes` for searches whose included evidence depends on full-text/PDF inspection.
- Excluded records must be traceable by citation, PMID/DOI, or local Zotero label when available, with a short exclusion reason such as `off-topic`, `wrong population`, `not direct evidence`, `metadata mismatch`, `duplicate`, `no full text`, or `contradicts claim`.

Required output structure:

```markdown
## Search Reproducibility
| Source | Query | Mode | Max results | Status | Included | Notes |
|---|---|---|---:|---|---:|---|
| Zotero | {semantic query} | semantic | {max_results or Not recorded} | Completed / No hits / Failed | {included_count} | full_text_inspected: yes/no/partial; included: {citation keys}; excluded: {record + reason} |
| Zotero | {keyword query} | keyword / structured | {max_results or Not recorded} | Completed / No hits / Failed | {included_count} | full_text_inspected: yes/no/partial; included: {citation keys}; excluded: {record + reason} |
| PubMed | {attempted or planned PubMed query} | PubMed | {max_results} | Completed / ⚠️ Tool unavailable; search not executed / Failed; query reported / Not executed | {included_count} | included PMIDs: {PMIDs or none}; excluded: {PMID/citation + reason}; failed reason: {if any}; full_text_inspected: yes/no/partial |
```

### Copy-ready vs Annotated Output

Every evidence package must separate manuscript-ready prose from evidence-review annotations.

`Copy-ready Manuscript Text` is the text users can copy directly into a manuscript:

- Preserve the manuscript's original language unless translation is explicitly requested.
- Do not include internal review notes, workflow explanations, QC comments, tool-status commentary, or phrases such as `citation should be verified`.
- Do not mention PubMed/Zotero execution status inside the copy-ready prose.
- Keep cautious wording required by evidence level and source layer.
- If evidence is insufficient, use hedge wording, knowledge-gap wording, or remove the unsupported claim.
- If a concept, citation, DOI/PMID, or claim is unverified, do not write it as established fact.
- Use only citations that are recommended and not blocked by metadata/citation warnings.

`Annotated Recommended Text` is the evidence-review explanation layer:

- It may explain citation placement, evidence level, source layer, caveats, reviewer risk, and metadata/tool limitations.
- It must identify which sentences or clauses are `Current study`, `Zotero external evidence`, `PubMed external evidence`, `Interpretive bridge`, or `Unsupported gap`.
- It should explain when a citation supports direct evidence, related evidence, mechanism, method, background, plausibility, or only a bridge inference.
- It may state that a citation, concept, DOI/PMID, or PubMed search requires verification.

Required output structure:

```markdown
## 2. 可直接使用的稿件文本（Copy-ready Manuscript Text）
> {manuscript-ready text only; no workflow notes or internal caveats}

## 3. 注释版推荐文本（Annotated Recommended Text）
| Sentence / clause | Recommended text | Source layer | Evidence level | Citation rationale | Caveat / reviewer risk |
|-------------------|------------------|--------------|----------------|--------------------|------------------------|
| ... | ... | Current study / Zotero external evidence / PubMed external evidence / Interpretive bridge / Unsupported gap | A / B / C / D / E | ... | ... |
```

### Markdown Report Requirements

The report must use Chinese-first user-facing headings and analytical prose by default, while preserving manuscript language and official bibliographic metadata according to **0. Durable Output Language Policy**. It must include these sections in order, including PubMed status even when PubMed was unavailable or failed:


1. `Metadata and Use Status`
2. `Critical Warnings`
3. `核心结论`
4. `可直接使用的稿件文本（Copy-ready Manuscript Text）`
5. `注释版推荐文本（Annotated Recommended Text）`
6. `主张—证据矩阵`
7. `引文放置建议`
8. `Evidence Logic Chain`
9. `参考文献表`
10. `Search Reproducibility`
11. `Zotero 检索总结`
12. `PubMed 扩展检索`
13. `综合写作建议`
14. `Claims to Revise or Remove`
15. `证据缺口与审稿风险`
16. `元数据质量控制`
17. `导出文件`

Add source and export-standardization detail to the `Reference Table` and `Metadata Quality Control` so the reader can tell whether evidence came from Zotero, PubMed, or both, and whether the RIS was standardized from PMID/PubMed, DOI metadata, or inspected source metadata.

Critical warning report rules:

- `Critical Warnings` must appear immediately after `Metadata and Use Status` and before `## 1. 核心结论（Bottom Line）`.
- Each warning must include `Affected claim`, `Risk`, and `Required action`.
- Critical warnings must include PubMed failures, missing direct evidence for central claims, contradictory evidence, unverified citations/concepts, unresolved metadata mismatch, duplicate selected references, current-study/external-evidence confusion, unsupported causal wording, unsupported BMI-independent wording, and unsupported horizontal pleiotropy wording.
- If no critical warnings apply, write exactly `No critical warnings`.

Search reproducibility report rules:

- `Search Reproducibility` must include Zotero semantic search, Zotero keyword/structured search, and PubMed search rows.
- Each row must record query, mode, max_results, status, included_count, and excluded_reason through the `Source`, `Query`, `Mode`, `Max results`, `Status`, `Included`, and `Notes` columns.
- PubMed failed or unavailable cases must record the attempted or planned PubMed query and failed reason.
- `Notes` must include included PMIDs when available, excluded records and reason, and `full_text_inspected: yes/no/partial`.

Reference canonicalization report rules:

- `Reference Canonicalization Gate` must be completed before `Metadata Quality Control` and before RIS export decisions are finalized.
- The gate may appear as an explicit subsection inside `元数据质量控制（Metadata Quality Control）` rather than as a separate top-level report section, so the public report preserves the required 17-section order.
- Every selected reference must check DOI, PMID, title, first author, and year.
- DOI- or PMID-identical records must be merged into one canonical record, with duplicate Zotero keys recorded.
- PubMed-vs-Zotero conflicts must be marked `Possible metadata mismatch` and unresolved mismatch must not enter RIS.
- RIS action must be exactly one of `Include`, `Exclude`, `Verify`, or `Optional`, with a reason for each action.

Copy-ready and annotated text rules:

- `Copy-ready Manuscript Text` must be directly copyable into the manuscript and must not contain internal review notes, workflow explanations, tool-status comments, or `citation should be verified` wording.
- `Annotated Recommended Text` must explain citation placement, source layer, evidence level, caveats, and reviewer risk in a table.
- Unsupported or unverified concepts must not be stated as facts in copy-ready text.
- Caveats, verification needs, PubMed failures, and metadata concerns belong in `Annotated Recommended Text`, `Gaps and Reviewer-risk Assessment`, or `Metadata Quality Control`, not inside copy-ready prose.

Evidence-level report rules:

- The Claim–Evidence Matrix must contain an `Evidence level` column using only `A`, `B`, `C`, `D`, or `E`.
- Citation Placement must carry forward the same evidence level used for the relevant claim.
- Reviewer-risk Assessment must state the evidence level in `Evidence basis` so risk judgments are traceable to the same A-E framework.
- Copy-ready Manuscript Text must be automatically hedged by level: A/B may be moderately confident; C uses plausibility wording; D uses current-study wording plus cautious external-evidence bridge language; E is removed, marked for verification in annotated/risk sections, or strongly hedged.

Evidence-boundary report rules:

- The Claim–Evidence Matrix must contain a `Source layer` column using only `Current study`, `Zotero external evidence`, `PubMed external evidence`, `Interpretive bridge`, or `Unsupported gap`.
- Citation Placement and Reviewer-risk Assessment must preserve the same source layer used for the relevant claim.
- Current-study findings must be written as current-study results, not as facts proven by citations.
- External evidence may support biological plausibility, prior association, method, or mechanism, but must not be used to prove SMR, TWAS, MAGMA, colocalization, enrichment, candidate-gene, or other current-study outputs.
- Interpretive bridge sentences must use cautious wording such as `consistent with`, `may suggest`, or `provide biological plausibility`.

Reference table rules:

- Do not expose Zotero item keys as the primary reading object.
- Hide item keys inside `[Item](zotero://select/items/0_{item_key})` links.
- Use `[PDF](zotero://open-pdf/library/items/{attachment_key})` when a PDF attachment key is available; otherwise use `—`.
- Use `[DOI](https://doi.org/{doi})` and `[PMID](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)` links when identifiers are available.
- Use `Not available` for unknown collection membership.

### Reference Canonicalization Gate

Before generating RIS, every selected reference must pass a canonical reference quality-control gate. This gate prevents duplicate keys, incorrect PMID/DOI linkage, abnormal author fields, metadata conflicts, and duplicate RIS export.

Reference canonicalization rules:

- Every selected reference must check DOI, PMID, title, first author, and year before RIS export.
- Every selected reference must record a canonical identifier: DOI / PMID / Zotero key. Prefer DOI when reliable, then PMID, then canonical Zotero key when no external identifier is available.
- If DOI or PMID is the same across candidates, merge them into one canonical record and export at most one RIS record.
- If multiple Zotero keys point to the same work, choose one canonical Zotero key and record all duplicate keys.
- Duplicate check result must be explicit: `unique`, `merged by DOI`, `merged by PMID`, `possible duplicate`, `duplicate excluded`, or `unresolved duplicate`.
- Metadata source of truth must be explicit: `PMID/PubMed`, `DOI metadata`, `Zotero metadata`, or `manual verification required`.
- If PubMed and Zotero metadata conflict for DOI, PMID, title, first author, or year, mark `Possible metadata mismatch`.
- RIS action must be exactly one of `Include`, `Exclude`, `Verify`, or `Optional`.
- Unresolved mismatch must not enter RIS; mark RIS action as `Verify` or `Exclude` until resolved.
- `Optional` is allowed only for relevant background or context references that are not required for the core manuscript claim.
- Each row must include a reason explaining the canonical identifier choice, duplicate decision, metadata source of truth, and RIS action.

Required output structure:

```markdown
## Reference Canonicalization Gate
| Selected reference | Canonical identifier | DOI | PMID | Title check | First author check | Year check | Canonical Zotero key | Duplicate keys | Duplicate check result | Metadata source of truth | RIS action | Reason |
|--------------------|----------------------|-----|------|-------------|--------------------|------------|----------------------|----------------|------------------------|--------------------------|------------|--------|
| Author Year | DOI / PMID / Zotero key: ... | matched / missing / conflict | matched / missing / conflict | matched / conflict | matched / conflict | matched / conflict | KEY | KEY2; KEY3 / none | unique / merged by DOI / merged by PMID / possible duplicate / duplicate excluded / unresolved duplicate | PMID/PubMed / DOI metadata / Zotero metadata / manual verification required | Include / Exclude / Verify / Optional | ... |
```

### Metadata Quality Control

Before writing RIS records, build a quality-control table for every candidate reference:

| Check | What to inspect | Markdown action | RIS action |
|-------|-----------------|-----------------|------------|
| Missing metadata | DOI, PMID, authors, year, journal, volume, issue, pages | Add `Missing metadata` warning with exact missing fields | Omit unknown fields; do not infer |
| Metadata mismatch | Zotero, PubMed, PMID-derived, and DOI-derived DOI, PMID, normalized title, year, journal | Add `Possible metadata mismatch` with conflicting values | Exclude until resolved unless the user explicitly accepts a canonical source |
| Duplicate warning | Same DOI/PMID/title or fuzzy author + year + journal across Zotero and PubMed | Add `Possible duplicate` and list candidate citations | Include only the selected canonical record |
| Evidence source | Whether the evidence record came from Zotero, PubMed, or both | Mark `Zotero`, `PubMed`, or `Zotero + PubMed` | Source label does not determine RIS metadata by itself |
| RIS standardization source | Which identifier/source supplied the final EndNote RIS fields | Mark `PMID/PubMed`, `DOI`, `Zotero metadata`, or `PubMed metadata` | Prefer PMID/PubMed, then DOI, then inspected source metadata |
| PubMed not executed | PubMed-capable tool unavailable | Mark `⚠️ Tool unavailable; search not executed` | Do not create PubMed-only RIS records |
| PubMed search failed | PubMed-capable tool was visible but returned an error | Mark `Failed; query reported` and include the attempted query/error briefly | Do not create PubMed-only RIS records |

### RIS Metadata Rules

RIS records must be generated from inspected metadata only.

| Source | Allowed metadata |
|--------|------------------|
| Selected reference with PMID | Prefer PMID/PubMed metadata for RIS standardization when retrieved |
| Selected reference with DOI but no PMID | Prefer DOI metadata for RIS standardization when retrieved |
| Zotero record without identifier-derived standardization | `zotero_get_item_metadata` output; DOI/PMID/ISBN from Zotero metadata |
| PubMed record without DOI standardization | PubMed returned metadata from a completed search |
| Missing field | Leave blank or omit; do not infer |
| Metadata conflict | Mark in Markdown report; exclude from RIS unless the conflict is resolved |

Zotero-to-RIS mapping:

| Zotero field | RIS field |
|--------------|-----------|
| `itemType` | `TY` (`journalArticle` -> `JOUR`; `book` -> `BOOK`; `conferencePaper` -> `CONF`; `preprint` -> `UNPB` or `JOUR` when already journal-indexed; `report` -> `RPRT`; `thesis` -> `THES`; `webpage` -> `ELEC`; `bookSection` -> `CHAP`; `dataset` -> `DATA`; `patent` -> `PAT`) |
| `creators` | `AU`, one line per author |
| `date` | `PY` and optionally `Y1` |
| `title` | `TI` |
| `publicationTitle` | `JO` / `T2` |
| `journalAbbreviation` | `J2` |
| `volume` | `VL` |
| `issue` | `IS` |
| `pages` | `SP` / `EP` when separable |
| `DOI` | `DO` |
| `PMID` | `AN` or `N1` |
| `url` | `UR` |
| `abstractNote` | `AB` when needed |
| `language` | `LA` |
| `tags` | `KW`, one line per retained scholarly keyword/tag |
| item key | `N1  - Zotero key: XXXXXXXX` only; do not show as citation text |

RIS tag compatibility rules:

- Filter out Zotero workflow/personal tags before writing `KW`, including tags that start with `/`, emoji-only tags, pure-symbol tags, and tags used only for local reading status.
- Keep scholarly subject tags such as MeSH terms, disease names, methods, exposures, and study-design terms.
- Use UTF-8 plain text, but avoid unusual symbols in RIS fields when an ASCII equivalent is available.
- If a creator name appears inverted or nonstandard, verify it against inspected Zotero/PubMed/DOI metadata before normalizing; otherwise disclose the issue in Markdown QC and exclude the record from RIS by default.

### Quality Gates

Before reporting success, check:

- Markdown report exists and includes metadata/use status, critical warnings immediately after metadata/use status, copy-ready manuscript text, annotated recommended text, Zotero search summary, a PubMed Expansion section with query and execution status, Search Reproducibility with Zotero semantic search, Zotero keyword/structured search, PubMed search, attempted/planned PubMed query when unavailable or failed, included PMIDs, excluded records and reasons, `full_text_inspected: yes/no/partial`, claim–evidence matrix, integrated writing advice, reviewer-risk assessment, Reference Canonicalization Gate, metadata quality-control section, and export file section.
- Metadata and Use Status records `Related prior packages` and `Run relationship rationale`; new reports may say `Potentially supersedes`, `Complementary to`, or `Related; supersession unclear`, but old reports are not automatically modified and project-level summary files are generated only when the user requests consolidation.
- Reference Canonicalization Gate checks DOI, PMID, title, first author, and year for every selected reference; records canonical identifier, canonical Zotero key, duplicate keys, duplicate check result, metadata source of truth, RIS action, and reason; merges same DOI/PMID records; blocks unresolved mismatch from RIS.
- Critical Warnings contains every high-risk issue that meets the trigger conditions and uses `Affected claim`, `Risk`, and `Required action`; if there are no critical warnings, it says exactly `No critical warnings`.
- Copy-ready Manuscript Text is directly copyable, preserves the manuscript language, and contains no internal review notes, workflow explanations, tool-status comments, or `citation should be verified` wording.
- Annotated Recommended Text explains citation placement, source layer, evidence level, caveats, and reviewer risk separately from the copy-ready prose.
- Metadata/use status includes exactly one package status: `Ready`, `Caution`, `Partial`, `Superseded`, or `Unknown`.
- Every claim in the claim–evidence matrix has a source layer and an A-E evidence level.
- Current-study findings, including SMR, TWAS, MAGMA, colocalization, enrichment, candidate-gene prioritization, and user-supplied statistical results, are marked as `Current study` and are not described as proven by external literature.
- Reviewer-risk assessment uses the same A-E evidence levels in the `Evidence basis` column when explaining risk.
- Copy-ready Manuscript Text is hedged according to evidence level: A/B can be moderately confident, C/D must be cautious, and E must be removed, verified, or strongly hedged.
- Copy-ready Manuscript Text separates current-study wording from external-evidence wording and uses interpretive bridge language when connecting the two.
- PubMed status truthfully reflects tool execution: `Completed` requires an actual completed PubMed search and inspected metadata; unavailable, failed, or not-executed searches must not be described as completed.
- PubMed-only RIS records are included only when the PubMed search completed and the record metadata was inspected.
- RIS file is plain RIS only, with no Markdown headings, explanations, comments, or code fences.
- Every RIS record starts with `TY  -` and ends with `ER  -`.
- Recommended Zotero citations use metadata consistent with Zotero.
- PubMed-only recommended citations use metadata consistent with completed PubMed search results; if PubMed was not executed, no PubMed-only RIS records are created.
- Missing metadata, metadata mismatch, and duplicate warning cases are disclosed in the Markdown report and not silently written into RIS.
- All generated-file paths shown in the report and final chat are relative paths; local absolute paths such as `/Users/...` are not allowed.

### Evidence Package QA Self-Check Prompt

The skill must run this internal QA prompt immediately before writing Markdown/RIS files and again after writing them. Use it as a gate, not as user-facing content. Do not announce completion until failures are corrected or explicitly reported as blocking warnings.

```text
你是一名科研 evidence package QA 工程师。请在 zotero-evidence-review skill 写入 Markdown 和 RIS 前执行自检。
检查：
1. Report 是否包含 Status、Critical Warnings、Copy-ready Manuscript Text；
2. Claim–Evidence Matrix 是否包含 Evidence level 和 Source layer；
3. 是否把 current-study finding 错写成 external evidence；
4. 是否存在 direct causality、BMI independence、horizontal pleiotropy 等过度表述；
5. PubMed status 是否真实反映工具执行情况；
6. PubMed-only RIS 是否只来自 completed PubMed search；
7. unresolved metadata mismatch 是否被排除出 RIS；
8. RIS 是否无 Markdown heading/code fence；
9. 所有路径是否为相对路径；
10. 若发现问题，先修正报告再宣布生成完成。
输出：内部自检清单，不必完整暴露给用户；最终 chat 只显示 status、paths 和 critical warnings。
```

Pre-write QA gate checklist:

- `Status`: Markdown report metadata and export section contain exactly one status from `Ready`, `Caution`, `Partial`, `Superseded`, or `Unknown`; final chat will repeat the same status.
- `Critical Warnings`: the section exists immediately after metadata/use status; it either contains a table with `Affected claim`, `Risk`, `Required action`, or exactly `No critical warnings`; warnings are consistent with package status.
- `Copy-ready Manuscript Text`: copy-ready text exists, preserves manuscript language, contains no internal QA/tool notes, and excludes unverifiable or unsupported assertions.
- `Claim evidence level`: every Claim–Evidence Matrix row has `Evidence level` using `A`, `B`, `C`, `D`, or `E`; Citation Placement and Reviewer-risk Assessment preserve the same level.
- `Source layer`: every claim-level row distinguishes `Current study`, `Zotero external evidence`, `PubMed external evidence`, `Interpretive bridge`, or `Unsupported gap`; current-study findings are not described as proved by external literature.
- `Overclaim control`: direct causality, BMI independence, horizontal pleiotropy, mediation/mechanism, and genetic-prioritization claims are hedged unless directly supported; E-level claims are removed, marked for verification, or strongly hedged rather than written as established facts.
- `PubMed status`: `Completed` is used only when PubMed search actually executed and relevant metadata was inspected; unavailable/failed/not-executed cases use the exact allowed status and include the planned or attempted query.
- `RIS provenance`: PubMed-only RIS records appear only when PubMed status is `Completed`; no PubMed-only RIS records are written for unavailable, failed, or planned-only PubMed searches.
- `Metadata mismatch`: unresolved metadata mismatch and unresolved duplicate records are disclosed in the report and excluded from RIS unless the user explicitly selected a canonical source.
- `RIS format`: RIS contains only RIS records; no Markdown headings, prose, comments, or code fences; every record starts with `TY  -` and ends with `ER  -`.
- `Relative paths`: Markdown report, Export File section, final chat, and any in-report links to generated files use relative paths only; no `/Users/...`, home-directory, or other local absolute paths.
- `Final response hygiene`: final chat displays only package status, generated relative paths, and critical warnings; do not expose the full internal checklist unless the user asks for debug details.

Post-write QA gate:

- Re-check the written Markdown and RIS against the same checklist before final response.
- If the post-write gate fails, correct the files first when safe; if correction is impossible, do not say the package is complete—return `Status: Partial` or `Unknown` with the blocking critical warning and paths to any partial files.

### Output Format

In chat, after files are written, output only:

```markdown
Generated Evidence Package:
- Status: Ready / Caution / Partial / Superseded / Unknown
- Critical warnings:
  - No critical warnings
  - `<affected claim>` — Risk: `<risk>`; Required action: `<required action>`
- Markdown report: `zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_evidence_review.md`
- EndNote RIS: `zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_references.ris`

Warnings:
- `<non-critical metadata/tool/status warning if any; otherwise omit this section>`
```

---

## 3. Citation Verification Protocol

Use when the user asks to verify whether a specific claim, quote, statistic, or citation is actually supported by a cited paper or reference. The protocol automatically detects the reference language and chooses the appropriate verification path.

### Language Detection

1. Retrieve Zotero metadata with `zotero_get_item_metadata` when an item key, title, DOI, or citation can be matched.
2. Determine language from the `language` field first.
3. If `language` is empty or ambiguous, infer from title, abstract, publication title, and full-text/attachment language.
4. Route automatically:
   - **English or non-Chinese scholarly literature** → Full-text PDF path.
   - **Chinese-language references**（期刊论文、图书、学位论文、政策文件）→ CNKI CDP / WebSearch path.
5. If the source language cannot be determined, state the uncertainty and choose the path most likely to verify the available bibliographic data.

### Shared Preflight

1. Confirm the exact claim, quote, statistic, or citation metadata to verify.
2. Confirm the target paper/reference from Zotero metadata or the user's supplied citation.
3. Estimate token budget for full-text verification: `Pages × 700 + 1000`.
4. Warn if remaining tokens < 50k.
5. Confirm whether full text, PDF attachment, abstract, notes, or external bibliographic pages are available.

### Path A: Full-text PDF Verification

Use for English or non-Chinese scholarly papers with full text available in Zotero.

1. Prefer read-only MCP page/full-text access first: use `zotero_read_pdf_pages` page ranges or `zotero_get_item_fulltext` when available, and keep the source in Zotero rather than exporting files.
2. If direct MCP page reading is unavailable and the environment permits temporary files, extract complete PDF text to a temporary file as a fallback; otherwise state which pages/sections could not be accessed.
3. Read every available page sequentially in 250-300 line chunks.
4. Record exact page/line locations for each claim, quote, and statistic.
5. Cross-check numerical data (N=X, p<0.05, CI, effect size, sample size) against the original.
6. Compare the user's claim against Zotero metadata, abstract, tables, figures, and author wording.
7. Judge whether the citation fully supports, partially supports, contradicts, or does not address the claim.

### Path B: Chinese Reference Verification

Use for Chinese-language references, including 中文期刊论文、图书、学位论文、政策文件.

#### Primary Method: CNKI CDP Direct Search

Use this route only when Chrome/CDP MCP browser tools are configured and available in the current environment:

1. Navigate to `kns.cnki.net/kns8s/AdvSearch`.
2. Check for CAPTCHA via screenshot, not snapshot text alone.
3. Enter the exact Chinese title into the search field.
4. Click search and wait for results.
5. Extract structured data from the results table.
6. Compare title / authors / journal or publisher / year.

#### Fallback: Multi-Source WebSearch

When CDP is unavailable and a WebSearch-capable tool is configured, execute all of the following:

1. `"<full title>"` exact match.
2. `<title> <author>` broader match.
3. `"<title>" site:cnki.net`.
4. `"<title>" site:wanfangdata.com.cn`.
5. `"<title>" site:xueshu.baidu.com`.

If neither CDP nor WebSearch tools are available, do not claim that CNKI or web verification was completed. Provide the exact searches above as manual verification queries and mark the route as `⚠️ Tool unavailable` until the user supplies results or enables the required tool.

#### Chinese Reference Verdicts

- **Confirmed**: exact title + author + journal/publisher + year all match.
- **Likely Real**: title matches and at least 2 of the remaining 3 metadata fields match.
- **Metadata Error**: the work exists but citation metadata is wrong.
- **Likely Fabricated**: no credible match after available CNKI/CDP and multi-source fallback checks.

Rules:
- Do NOT claim "Uncertain (needs CNKI verification)" as a final verdict.
- No DOI ≠ fabricated; most Chinese papers lack DOIs.
- Always give a definitive verdict: Confirmed / Likely Real / Metadata Error / Likely Fabricated.

### Self-Audit Checklist

Before claiming "verification complete":
- [ ] Retrieved and inspected Zotero metadata when available.
- [ ] Detected or inferred source language.
- [ ] Used the correct verification path for the source language.
- [ ] For full-text papers: read complete text or clearly stated which pages/sections were available.
- [ ] Located page/line evidence for all checked claims where full text is available.
- [ ] Verified numerical data (N, p value, CI, effect size, dates, page numbers) when relevant.
- [ ] Checked author wording and avoided overstating association as causation.
- [ ] For Chinese references: checked CNKI CDP or all required fallback searches.
- [ ] Stayed within token budget or warned the user before proceeding.

### Output Format

Output format: see **Appendix: Output Templates → VERIFICATION_REPORT**.

---

## 4. Chinese Academic Writing Rules

When responding in Chinese:

- Keep article titles, journal names, author names, DOI, PMID, and item keys in English.
- Do not translate official paper titles unless the user asks.
- Distinguish association, causation, mediation, prediction, and mechanism.
- Use cautious wording when evidence is indirect, observational, or inconsistent.
- Do not use a Zotero item as evidence unless its metadata, abstract, full text, note, or annotation has been inspected.
- Clearly mark whether each citation is for background, method, mechanism, or direct empirical evidence.
- When the evidence is insufficient, suggest hedging: "可能"、"提示"、"与…相关" rather than "证明"、"导致".

### Output Formatting Rule

- Prefer tables over nested bullet lists. List each paper's full metadata (title/journal/DOI/link) **once** in a reference table or Refs block; everywhere else cite as `Author Year (KEY)`.
- Never repeat the same paper's bibliographic block across multiple sections.
- Reserve prose bullets for caveats, wording fixes, and gaps — not for restating table contents.

---

## 5. External Source Fallback

When Zotero returns insufficient results, first check which external-search tools are configured in the current environment. Do not imply that any external MCP server is available unless its tools are actually present.

Potential free MCP servers that may be useful when installed:

| Source | Covers | API Key | Best for |
|--------|--------|---------|----------|
| crossref-academic-mcp-server | Crossref + OpenAlex + Semantic Scholar | None | DOI lookup, citation graph, author profile |
| paper-search-mcp | arXiv + PubMed + bioRxiv | None | Preprints, biomedical literature |
| academix | OpenAlex + DBLP + Semantic Scholar + arXiv + CrossRef | None | CS/AI/ML papers, multi-source aggregation |

### Workflow

1. Search Zotero first.
2. If insufficient, identify available external-search tools.
3. If suitable external tools are available, search them and mark all external results with source labels.
4. If no suitable external tools are available, provide ready-to-copy external search queries and say that the search was not executed.
5. Ask the user whether to add found papers to Zotero.
6. Before adding, ask where to place the items:
   - current collection, when a current collection key/name is known;
   - a specified collection name/key provided by the user;
   - main library only.
7. Use `zotero_add_by_doi` or `zotero_add_by_url` with the `collections` parameter when a target collection is confirmed.

---

## Usage Examples

Use short prompts. `/zotero-evidence-review` is the easiest way to call this skill; the workflow is chosen automatically from the request.

### Search

> "/zotero-evidence-review 搜 Zotero 里关于肠道菌群和抑郁症的文献"

The skill will:
1. Expand to: `semantic_search("gut microbiota depression Mendelian randomization")` + `search_library(q="gut microbiota depression MR", tags=["Mendelian Randomization", "depression"])`
2. Return combined results with similarity scores and Zotero links

### Paragraph Evidence & Citation Analysis

> "/zotero-evidence-review 帮我给下面这段草稿找证据并补引用：
> '慢性炎症通过激活 JAK-STAT 信号通路促进动脉粥样硬化斑块形成，而 IL-6 受体阻断剂可显著降低心血管事件风险。'"

The skill will treat this as citation-support work unless the user explicitly says `不要生成文件`, `只在聊天输出`, `不导出`, or `chat only`:
1. Route the paragraph to Module 2 and extract claims: (a) chronic inflammation → JAK-STAT → atherosclerosis, (b) IL-6R blockade → reduced CVD risk.
2. Build one batch query set and run Zotero semantic search plus one keyword fallback if needed.
3. Reuse the same result pool for Layer A (claim-evidence matrix), Layer B (sentence-level citation recommendations), and the diff paragraph.
4. Continue to Module 2.5 in the full **Paragraph Citation Package Workflow (Module 2 + Module 2.5)**: collect Zotero metadata/PDF links, attempt automatic PubMed expansion after Zotero local search when a PubMed-capable tool is configured and visible, run matching/QC, and write the Markdown report plus EndNote RIS.
5. If the user opted out of files, stop after the chat-only Module 2 output and ask whether to start external search for remaining gaps.

### Strict Verification

> "请验证'IL-6 受体阻断剂可降低心血管事件风险'这句话，确认原文确实这么说了"

The skill will:
1. Extract claim: IL-6R blockade → reduced CVD risk
2. Find the cited paper in Zotero
3. Extract and read full PDF sequentially
4. Report exact line number and quote
5. Judge: fully supports / partially supports / does not support

### Paragraph Citation Insertion

> "/zotero-evidence-review 帮我润色这段讨论，并补充合适的引用：
> '我们的研究发现某基因与 2 型糖尿病之间存在显著关联。这一结果与以往研究一致。'"

The skill will:
1. Route the pasted paragraph to Module 2
2. Search once for relevant genetic association studies in the library
3. Recommend sentence-level citations and explain the citation rationale
4. Suggest more precise wording using diff format when the evidence requires hedging
5. Continue to Module 2.5 and generate the Markdown evidence report plus EndNote RIS unless the prompt says `不要生成文件`, `只在聊天输出`, `不导出`, or `chat only`

Chat-only example:

> "/zotero-evidence-review 只在聊天输出，不要生成文件：帮我给这段草稿找证据并补引用。"

---

## Notes

- Always prefer **semantic search** first for conceptual queries.
- For author/year specific lookups, use keyword search with exact fields.
- Zotero links use the format: `zotero://select/items/0_{ItemKey}`
- If the user has not built the semantic index yet, prompt them to run `zotero-mcp update-db`.
- If full-text is needed, suggest `zotero-mcp update-db --fulltext`.
- Token budget for full verification: estimate 700 tokens per page + 1000 overhead.

---

## Appendix: Output Templates

Use these named templates whenever a module references an appendix template. For chat-only outputs, keep full bibliographic metadata in `REFS_BLOCK` only; elsewhere cite papers as `Author Year (KEY)`. For evidence packages, use `EVIDENCE_REVIEW_REPORT` plus `RIS_REFERENCE_FILE`.

### REFS_BLOCK

```markdown
**Refs**
- `KEY` — Author (Year). *Title*. *Journal* volume(issue):pages. DOI/PMID/URL. `zotero://select/items/0_KEY`
```

Rules:
- Full metadata appears exactly once.
- Include DOI when available; use PMID or URL when DOI is unavailable.
- Do not repeat title/journal/DOI in claim matrices or recommendation tables.

### CLAIM_EVIDENCE_MATRIX

```markdown
| # | 主张 | Source layer | Evidence level | 最佳引文 | Evidence type | Gap? |
|---|------|--------------|----------------|---------|---------------|------|
| 1 | X与Y相关 | Zotero external evidence | A | Wang 2022 (KEY) | 直接证据 | 否 |
| 2 | 本研究发现Z与W相关 | Current study | D | Li 2023 (KEY2) | 背景/机制支持；不能作为当前研究结果的直接证明 | 否，但需谨慎表述 |
| 3 | 当前结果可能与既往机制一致 | Interpretive bridge | C | Chen 2021 (KEY3) | 机制合理性 | 否，但需 bridge wording |
| 4 | Z导致W且独立于BMI | Unsupported gap | E | — | 未验证 / 无直接证据 | ⚠️ 是 |
```

Rules:
- One row per extracted claim.
- Use claim IDs consistently in gap handling and sentence-level recommendations.
- `Source layer` must be exactly one of `Current study`, `Zotero external evidence`, `PubMed external evidence`, `Interpretive bridge`, or `Unsupported gap`.
- `Evidence level` must be exactly one of `A`, `B`, `C`, `D`, or `E` as defined in **Module 2 → Unified Evidence Level**.
- `Evidence type` should describe the support role, e.g. `直接证据`, `相近直接证据`, `间接机制证据`, `背景证据`, `current-study only`, `contradicted`, or `requires verification`.
- Mark unsupported, contradicted, or insufficiently verified claims as `Unsupported gap`, evidence level `E`, and `Gap? = ⚠️ 是`.
- Mark current-study findings as `Current study` and evidence level `D` unless external literature directly replicates the same finding in a comparable study.
- External evidence used only for mechanism/background must be represented as `Interpretive bridge` or evidence level C/D, not as proof of the current-study finding.
- Evidence level C or D requires hedge wording in manuscript recommendations; evidence level E requires removal, verification, or strong hedging.

### WRITING_SUGGESTIONS_TABLE

```markdown
| 句子（前15字） | 推荐引文 | Source layer | Evidence level | 引用理由 |
|--------------|---------|--------------|----------------|---------|
| "慢性炎症通过…" | Wang 2022 (KEY) | Zotero external evidence | A | 直接证据；支持炎症通路与结局相关 |
| "我们的SMR发现…" | Li 2023 (KEY2) | Current study / Interpretive bridge | D | 当前研究发现只能由本研究表述；引用仅支持机制合理性 |
| "IL-6受体阻断…" | — | Unsupported gap | E | ⚠️ 库内无直接证据；建议改为更谨慎表述并外部检索 |
```

Rules:
- One row per sentence, not one row per paper.
- `Source layer` must match the most relevant claim in `CLAIM_EVIDENCE_MATRIX`; if a sentence connects current-study output to external evidence, mark the boundary explicitly as `Current study / Interpretive bridge`.
- `Evidence level` must match the most relevant claim in `CLAIM_EVIDENCE_MATRIX`; if a sentence combines multiple claims, use the most conservative level.
- Fold citation-addition, rewording, context, replacement, gap, and terminology advice into the `引用理由` column.
- Prefer a minimal set of high-value citations rather than citation stuffing.

### DIFF_REVISED_PARAGRAPH

```markdown
<!-- diff 格式规则：
  - 删除的词/短语：用 ~~删除~~ 标注
  - 新增的词/短语：用 **新增** 标注
  - 未改动内容保持原样
  - 段落末尾附改动摘要："改动：+N词/-M词，修改原因：[简短说明]"
-->
> 原文改动：~~证明~~ **提示** X 与 Y 相关 **Wang 2022 (KEY)**，并通过 Z 通路影响 W **Li 2023 (KEY2)**。
>
> 改动：+2引用/+1限定词/-1强因果词，修改原因：库内证据支持关联和机制线索，但不足以支持强因果表述。
```

Rules:
- Use `~~删除~~` only for text that should be removed or weakened.
- Use `**新增**` for inserted citations, hedges, qualifiers, or terminology changes.
- Leave unchanged text unmarked.

### EVIDENCE_REVIEW_REPORT

```markdown
# 证据综述：{topic}

## 1. Metadata and Use Status

来源：Zotero 本地库；PubMed: {Completed / ⚠️ Tool unavailable; search not executed / Failed; query reported / Not executed only for explicit chat-only or non-PubMed workflows}

| Field | Value |
|-------|-------|
| 生成日期 | {YYYY-MM-DD} |
| Package status | Ready / Caution / Partial / Superseded / Unknown |
| Status rationale | {one sentence explaining the main trigger for this status} |
| User guidance | {可直接用于写作 / 必须使用 hedge wording / 不建议作为最终证据包 / 仅保留历史记录 / 需要人工检查} |
| Related prior packages | {none / path + date + topic slug + relationship: Potentially supersedes / Complementary to / Related; supersession unclear} |
| Run relationship rationale | {topic slug similarity; core keyword overlap; selected references overlap; DOI/PMID overlap; manuscript section relationship} |
| 来源 | Zotero 本地库；PubMed: {Completed / ⚠️ Tool unavailable; search not executed / Failed; query reported / Not executed only for explicit chat-only or non-PubMed workflows} |
| 输入 | {user paragraph, claim, or search question} |

## 2. Critical Warnings
| Affected claim | Risk | Required action |
|----------------|------|-----------------|
| ... | PubMed unavailable / no direct evidence / contradiction / unverified citation or concept / metadata mismatch / duplicate record / current-study vs external-evidence confusion / unsupported causal wording / unsupported BMI-independent claim / unsupported horizontal pleiotropy claim | Revise wording / verify citation / remove claim / complete PubMed search / resolve metadata / deduplicate records / mark as current-study only |

If no critical warnings apply, write exactly:

No critical warnings

## 3. 核心结论（Bottom Line）
- {1-3 句中文证据判断；如稿件原文为英文，可在中文判断后保留必要英文术语}

## 4. 可直接使用的稿件文本（Copy-ready Manuscript Text）
> {manuscript-ready text only; preserve the manuscript's original language unless translation is requested; hedge according to A-E evidence level; do not include workflow notes, internal caveats, or verification reminders}

## 5. 注释版推荐文本（Annotated Recommended Text）
| Sentence / clause | Recommended text | Source layer | Evidence level | Citation rationale | Caveat / reviewer risk |
|-------------------|------------------|--------------|----------------|--------------------|------------------------|
| ... | ... | Current study / Zotero external evidence / PubMed external evidence / Interpretive bridge / Unsupported gap | A / B / C / D / E | ... | ... |

## 6. 主张—证据矩阵（Claim–Evidence Matrix）
| # | Claim | Source layer | Evidence level | Zotero evidence | PubMed evidence | Evidence status | Confidence | Risk | Recommended action | Recommended citation |
|---|-------|--------------|----------------|-----------------|-----------------|-----------------|------------|------|--------------------|----------------------|
| 1 | ... | Current study / Zotero external evidence / PubMed external evidence / Interpretive bridge / Unsupported gap | A / B / C / D / E | Author Year / none | PubMed confirms / not searched / no direct evidence | supported / partly supported / current-study only / bridge only / gap / needs verification | High / Medium / Low | Low / Medium / High | keep / hedge / move to annotated text / remove / verify / mark as knowledge gap | Author Year / none |

## 7. 引文放置建议（Citation Placement）
| 句子 / 位置 | 推荐引文 | 用途 | Source layer | Evidence level | 措辞建议 |
|-------------|----------|------|--------------|----------------|----------|
| ... | Author Year | background / direct / method / caveat / bridge | Current study / Zotero external evidence / PubMed external evidence / Interpretive bridge / Unsupported gap | A / B / C / D / E | ... |

## 8. Evidence Logic Chain
| Step | Current-study element | External evidence link | Source layer | Evidence level | Inference limit |
|------|-----------------------|------------------------|--------------|----------------|-----------------|
| 1 | {e.g., SMR/TWAS/MAGMA/colocalization/enrichment/current finding} | {citation or none} | Current study / Zotero external evidence / PubMed external evidence / Interpretive bridge / Unsupported gap | A / B / C / D / E | {what can and cannot be inferred} |

## 9. 参考文献表（Reference Table）
| # | Citation | Year | Study type | Main use | Evidence source | Zotero | PDF | DOI | PMID | Collection |
|---|----------|------|------------|----------|-----------------|--------|-----|-----|------|------------|
| 1 | Author et al., *Journal* | 2024 | Systematic review | ... | Zotero / PubMed / Zotero + PubMed | [Item](zotero://select/items/0_KEY) | [PDF](zotero://open-pdf/library/items/ATTACHMENT_KEY) | [DOI](https://doi.org/10.xxxx/xxxx) | [PMID](https://pubmed.ncbi.nlm.nih.gov/PMID/) | Collection name |

## 10. Search Reproducibility
| Source | Query | Mode | Max results | Status | Included | Notes |
|---|---|---|---:|---|---:|---|
| Zotero | {semantic query} | semantic | {max_results or Not recorded} | Completed / No hits / Failed | {included_count} | full_text_inspected: yes/no/partial; included: {citation keys}; excluded: {record + reason} |
| Zotero | {keyword query} | keyword / structured | {max_results or Not recorded} | Completed / No hits / Failed | {included_count} | full_text_inspected: yes/no/partial; included: {citation keys}; excluded: {record + reason} |
| PubMed | {attempted or planned PubMed query} | PubMed | {max_results} | Completed / ⚠️ Tool unavailable; search not executed / Failed; query reported / Not executed | {included_count} | included PMIDs: {PMIDs or none}; excluded: {PMID/citation + reason}; failed reason: {if any}; full_text_inspected: yes/no/partial |

## 11. Zotero 检索总结（Zotero Search Summary）
| 检索路径 | Query | Hits | Included | 备注 |
|----------|-------|-----:|---------:|------|
| Semantic search | ... | 0 | 0 | ... |

## 12. PubMed 扩展检索（PubMed Expansion）
日期：{YYYY-MM-DD}
数据库：PubMed
状态：Completed / ⚠️ Tool unavailable; search not executed / Failed; query reported

检索式：`{copyable PubMed query}`

| # | Citation | PMID | DOI | In Zotero? | Evidence use | Recommendation |
|---|----------|------|-----|------------|--------------|----------------|
| 1 | Author et al., Year | [PMID](https://pubmed.ncbi.nlm.nih.gov/PMID/) | [DOI](https://doi.org/10.xxxx/xxxx) | Yes / No / Possible mismatch | ... | Use / Consider importing / Exclude |

## 13. 综合写作建议（Integrated Writing Advice）
### 原始主张
{original text}

### Zotero 证据
- ...

### PubMed 证据
- ...

### 推荐修改
> ...

### 为什么这样表述更安全
...

## 14. Claims to Revise or Remove
| Claim | Problem | Evidence level | Source layer | Required revision |
|-------|---------|----------------|--------------|-------------------|
| ... | unsupported / overconfident / current-study miscast as external evidence / metadata unresolved | A / B / C / D / E | Current study / Zotero external evidence / PubMed external evidence / Interpretive bridge / Unsupported gap | hedge / remove / verify / move to gap statement |

## 15. 证据缺口与审稿风险（Gaps and Reviewer-risk Assessment）
| Affected claim / sentence | Risk | Severity | Evidence basis | Suggested fix |
|---------------------------|------|----------|----------------|---------------|
| ... | ... | High / Moderate / Low | Source layer: Current study / Interpretive bridge / Unsupported gap; Evidence level A / B / C / D / E; ... | ... |

## 16. 元数据质量控制（Metadata Quality Control）

### Reference Canonicalization Gate
| Selected reference | Canonical identifier | DOI | PMID | Title check | First author check | Year check | Canonical Zotero key | Duplicate keys | Duplicate check result | Metadata source of truth | RIS action | Reason |
|--------------------|----------------------|-----|------|-------------|--------------------|------------|----------------------|----------------|------------------------|--------------------------|------------|--------|
| Author Year | DOI / PMID / Zotero key: ... | matched / missing / conflict | matched / missing / conflict | matched / conflict | matched / conflict | matched / conflict | KEY | KEY2; KEY3 / none | unique / merged by DOI / merged by PMID / possible duplicate / duplicate excluded / unresolved duplicate | PMID/PubMed / DOI metadata / Zotero metadata / manual verification required | Include / Exclude / Verify / Optional | Canonical identifier chosen after DOI, PMID, title, first author, and year checks; Possible metadata mismatch if conflicts remain |

### Metadata QC Table
| Citation | Missing metadata | Metadata mismatch | Duplicate warning | Evidence source | RIS standardization source | RIS action |
|----------|------------------|-------------------|-------------------|-----------------|----------------------------|------------|
| Author Year | DOI / PMID / pages / none | Possible metadata mismatch: Zotero DOI ... vs PubMed DOI ... / none | Possible duplicate with Author Year / none | Zotero / PubMed / Zotero + PubMed | PMID/PubMed / DOI / Zotero metadata / PubMed metadata | Include / exclude / needs manual check |

## 17. 导出文件（Export File）
- Markdown report: `zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_evidence_review.md`
- EndNote RIS: `zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_references.ris`
- Evidence source: Zotero local library and PubMed expansion are separate evidence steps; combined results are deduplicated by DOI/PMID/title when available.
- Package status: Ready / Caution / Partial / Superseded / Unknown.
- Status rationale: {main trigger for the assigned status}.
- RIS standardization source: PMID/PubMed metadata when available and retrieved; DOI metadata when PMID is unavailable and DOI lookup succeeded; otherwise inspected Zotero or PubMed source metadata.
- RIS inclusion rule: final recommended citations only; low-relevance hits excluded.
- Metadata warnings: {missing fields, mismatches, duplicate warnings, or none}
```

Rules:
- Keep Zotero item keys hidden in links or notes, not as primary citation labels.
- If a PDF attachment is unavailable, use `—` in the PDF column.
- If collection membership is unknown, use `Not available`.
- If PubMed was not actually searched, clearly mark the status and include only the planned or attempted query, not invented results.
- Always include the metadata quality-control table; use `none` when there are no missing metadata, metadata mismatch, or duplicate warning cases.
- Every claim-level table in the report must use the same source layer definitions from Module 2; do not merge current-study findings and external evidence into a single unsupported proof statement.
- Every claim-level table in the report must use the same A-E evidence level definitions from Module 2; do not introduce alternate strength scales such as `strong/moderate/weak` without also mapping them to A-E.

### RIS_REFERENCE_FILE

```ris
TY  - JOUR
AU  - Last, First
PY  - 2024
Y1  - 2024/01/01
TI  - Article title
JO  - Journal name
J2  - Journal abbreviation
VL  - 12
IS  - 3
SP  - 100
EP  - 110
DO  - 10.xxxx/xxxx
AN  - PMID
UR  - https://doi.org/10.xxxx/xxxx
KW  - Zotero tag
N1  - Zotero key: XXXXXXXX
ER  -
```

Rules:
- The RIS file must contain RIS records only; no Markdown headings, prose, code fences, or comments.
- Every record starts with `TY  -` and ends with `ER  -`.
- Use one `AU  -` line per author and one `KW  -` line per retained scholarly keyword/tag.
- Filter out personal/workflow tags before writing `KW`, including emoji-only tags, pure-symbol tags, tags beginning with `/`, and local reading-status tags.
- Split page ranges into `SP` and `EP` when possible; if not possible, write the original page string to `SP` and omit `EP`.
- Omit unknown fields rather than guessing.
- Add `N1  - Zotero key: XXXXXXXX` for Zotero items only.
- PubMed-only records require metadata from an actually completed PubMed search; when PubMed is unavailable, do not create PubMed-only RIS records.
- Exclude unresolved metadata mismatch and unresolved duplicate warning records unless the user explicitly selects the canonical record.

### VERIFICATION_REPORT

```markdown
## Verification Report

| Claim / citation | Paper / reference | Path | Evidence location | Support level / verdict | Issue |
|------------------|-------------------|------|-------------------|-------------------------|-------|
| "X causes Y" | Author 2020 | Full-text PDF | p. 6 / line 436 | Partial support | supports association, not causation |
| "N=500" | Author 2021 | Full-text PDF | p. 3 / line 152 | ✅ Correct | — |
| 中文题名 + 作者 + 年份 | 中文期刊 | CNKI/WebSearch | CNKI result row | Confirmed | — |
```

Rules:
- `Path` must identify the verification route: `Full-text PDF`, `CNKI`, `WebSearch`, or another explicit route.
- `Evidence location` should include page/line when full text is available, or result source/row when verifying Chinese bibliographic metadata.
- `Support level / verdict` must be decisive: fully supported, partially supported, contradicted, not addressed, Confirmed, Likely Real, Metadata Error, or Likely Fabricated.
