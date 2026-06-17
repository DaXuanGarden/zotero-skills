---
name: zotero-evidence-review
description: Search, analyze, and verify citations in your Zotero library using semantic search, evidence-chain extraction, full-text citation verification, and writing suggestions grounded in your collection. Requires Zotero MCP to be configured.
license: MIT
compatibility: opencode,zcode
metadata:
  workflow: academic-research
  requires: zotero-mcp
  version: 2.0.1
---

# Zotero Evidence Review Skill

## Overview

Use Zotero MCP tools to search the user's Zotero library intelligently. This skill combines **semantic search** (concept matching via embeddings) with **keyword/structured search**, performs **paragraph evidence and citation analysis** from draft text, and verifies **citations against full text**.

---

## 0. Intent Detection

Route the user's request before choosing tools. Use the input shape and explicit trigger words; do not ask the user to choose a mode when the intent is clear.

| Intent | User input features | Route to |
|--------|---------------------|----------|
| `search` | Keywords, concepts, natural-language questions, broad topic discovery, or requests such as "search", "find papers", "what literature do I have about…" | **Module 1: Semantic + Structured Search** |
| `paragraph` | A pasted manuscript paragraph, draft section, or multi-sentence passage — regardless of whether the user says "find evidence", "build evidence chain", "add citations", "补引用", or "润色并补文献" | **Module 2: Paragraph Evidence & Citation Analysis** |
| `verify` | Words such as "verify", "核实", "check", "confirm" plus a specific citation/paper and a concrete claim, quote, statistic, or citation-supported statement | **Module 3: Citation Verification Protocol** |
| `health` | "library status", "库状态", "health check", "健康检查", "preflight", "index status", or questions about Zotero database readiness | **Module 0.5: Library Health Check** |

### Routing Rules

1. **Pasted paragraph always wins**: if the user provides a paragraph, route to `paragraph` / Module 2. Do not split it into separate "evidence chain" versus "writing suggestions" modes.
2. **Verification requires specificity**: only route to `verify` when both a cited source (or item key/DOI/title) and a claim/quote/statistic are present. Otherwise, route to `search` or ask a clarification.
3. **Health check is read-only by default**: route health/status requests to Module 0.5 and do not run repair actions unless the user explicitly confirms them.
4. **Ambiguous intent**: if the request cannot be confidently routed, output this numbered menu and ask the user to choose:

```markdown
我可以按以下哪种方式处理？
1. 语义+结构搜索（关键词/概念/问句）
2. 段落证据与引文分析（粘贴段落、找证据、补引用）
3. 精确核实（具体引用 + 具体主张/数据/引文）
4. 库健康度检查（库状态、索引、PDF覆盖率）
```

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
- **Metadata, abstracts, BibTeX/JSON export** → `zotero_get_item_metadata`.
- **Full text** → `zotero_get_item_fulltext` or `zotero_read_pdf_pages`.
- **Annotations and reading notes** → `zotero_get_annotations` and `zotero_get_notes`.
- **Collection-level search** → `zotero_get_collections`, `zotero_search_collections`, `zotero_get_collection_items`.
- **Semantic database status** → `zotero_get_search_database_status`.
- **Semantic database update** → `zotero_update_search_database`. Only when needed; prefer incremental `update-db`.

## Safety Rules

Always ask for explicit confirmation before:

- deleting Zotero items, notes, or annotations;
- merging duplicate items;
- batch-updating tags;
- moving many items between collections;
- force-rebuilding the semantic database;
- adding many items at once;
- overwriting notes or annotation comments.

Never fabricate citations, titles, authors, years, journal names, DOI, PMID, or Zotero item keys.
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

- **Layer A: evidence quality** — each extracted claim receives support strength and gap status.
- **Layer B: citation recommendation** — each sentence receives recommended citations and a concise citation rationale.

Do not repeatedly search Zotero for each output layer. Do not ask the user to choose between "find evidence" and "add citations" modes.

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
   - **Layer A: Claim-evidence matrix** — map each claim to the best available citation(s), support strength, and gap status.
   - **Layer B: Sentence-level citation recommendations** — map each sentence to the citation(s) that should be inserted and explain why.
4. **Diff paragraph**
   - Provide a revised paragraph showing citation insertions and necessary wording changes.
   - Mark deletions with `~~strikethrough~~` and additions with `**bold**`.
   - Keep unchanged text unmarked so the user can see exactly what changed.
   - End with a change summary in this format: `改动：+N词/-M词，修改原因：[简短说明]`.
5. **Gap summary + external search handoff**
   - Summarize claims with no adequate Zotero evidence.
   - For each gap, propose an external search query.
   - Ask whether to start external search using the workflow in **External Source Fallback**.

### Evidence and Rationale Labels

Use these labels inside the tables, especially in the "Strength" and "Citation rationale" columns:

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

When any row in the Layer A claim-evidence matrix has `Gap? = ⚠️ 是`, automatically enter the gap-handling flow after presenting the paragraph analysis.

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
- If evidence is indirect, mixed, observational, or mechanistic only, recommend hedging language rather than causal wording.
- Use the same Zotero result pool for both Layer A and Layer B; only search again if the user explicitly requests deeper follow-up.
- Do not fabricate missing support. Mark gaps clearly and hand off to external search only after asking.

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

1. Extract complete PDF text to a temporary file or read pages with `zotero_read_pdf_pages`.
2. Read every page sequentially in 250-300 line chunks.
3. Record exact page/line locations for each claim, quote, and statistic.
4. Cross-check numerical data (N=X, p<0.05, CI, effect size, sample size) against the original.
5. Compare the user's claim against Zotero metadata, abstract, tables, figures, and author wording.
6. Judge whether the citation fully supports, partially supports, contradicts, or does not address the claim.

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

### Search

> "帮我搜一下 Zotero 里关于肠道菌群与抑郁症的孟德尔随机化研究"

The skill will:
1. Expand to: `semantic_search("gut microbiota depression Mendelian randomization")` + `search_library(q="gut microbiota depression MR", tags=["Mendelian Randomization", "depression"])`
2. Return combined results with similarity scores and Zotero links

### Paragraph Evidence & Citation Analysis

> "以下是一段草稿，请帮我找证据链并补引用：
> '慢性炎症通过激活 JAK-STAT 信号通路促进动脉粥样硬化斑块形成，而 IL-6 受体阻断剂可显著降低心血管事件风险。'"

The skill will:
1. Split sentences and extract claims: (a) chronic inflammation → JAK-STAT → atherosclerosis, (b) IL-6R blockade → reduced CVD risk
2. Build one batch query set and run semantic search plus one keyword fallback if needed
3. Reuse the same result pool for Layer A (claim-evidence matrix) and Layer B (sentence-level citation recommendations)
4. Return a diff paragraph with new citation locations and any necessary hedging
5. Summarize gaps and ask whether to start external search

### Strict Verification

> "请验证'IL-6 受体阻断剂可降低心血管事件风险'这句话，确认原文确实这么说了"

The skill will:
1. Extract claim: IL-6R blockade → reduced CVD risk
2. Find the cited paper in Zotero
3. Extract and read full PDF sequentially
4. Report exact line number and quote
5. Judge: fully supports / partially supports / does not support

### Paragraph Citation Insertion

> "帮我润色这段讨论，并补充合适的引用：
> '我们的研究发现某基因与 2 型糖尿病之间存在显著关联。这一结果与以往研究一致。'"

The skill will:
1. Route the pasted paragraph to Module 2
2. Search once for relevant genetic association studies in the library
3. Recommend sentence-level citations and explain the citation rationale
4. Suggest more precise wording using diff format when the evidence requires hedging

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

Use these named templates whenever a module references an appendix template. Keep full bibliographic metadata in `REFS_BLOCK` only; elsewhere cite papers as `Author Year (KEY)`.

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
| # | 主张 | 最佳引文 | 强度 | Gap? |
|---|------|---------|------|------|
| 1 | X与Y相关 | Wang 2022 (KEY) | 强；直接证据 | 否 |
| 2 | Z导致W | — | — | ⚠️ 是 |
```

Rules:
- One row per extracted claim.
- Use claim IDs consistently in gap handling and sentence-level recommendations.
- Strength should combine support level and evidence type, e.g. `强；直接证据`, `中；间接机制证据`, `弱；背景证据`.
- Mark unsupported or insufficiently supported claims as `⚠️ 是`.

### WRITING_SUGGESTIONS_TABLE

```markdown
| 句子（前15字） | 推荐引文 | 引用理由 |
|--------------|---------|---------|
| "慢性炎症通过…" | Wang 2022 (KEY) | 直接证据；支持炎症通路与结局相关 |
| "IL-6受体阻断…" | — | ⚠️ 库内无直接证据；建议改为更谨慎表述并外部检索 |
```

Rules:
- One row per sentence, not one row per paper.
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
