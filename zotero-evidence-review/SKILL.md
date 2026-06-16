---
name: zotero-evidence-review
description: Search, analyze, and verify citations in your Zotero library using semantic search, evidence-chain extraction, full-text citation verification, and writing suggestions grounded in your collection. Requires Zotero MCP to be configured.
license: MIT
compatibility: opencode,zcode
metadata:
  workflow: academic-research
  requires: zotero-mcp
  version: 2.0.0
---

# Zotero Evidence Review Skill

## Overview

Use Zotero MCP tools to search the user's Zotero library intelligently. This skill combines **semantic search** (concept matching via embeddings) with **keyword/structured search**, helps **build evidence chains** from draft text, verifies **citations against full text**, and provides **citation-grounded writing suggestions**.

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

Each result entry includes:

```markdown
### N. Title
- **Authors**: ...
- **Year**: ...
- **Journal/Venue**: ...
- **DOI/PMID**: ...
- **Zotero item key**: ...
- **Zotero link**: zotero://select/items/0_ITEMKEY
- **Match type**: semantic / keyword / tag / collection
- **Similarity score**: ...
- **Evidence role**: background / mechanism / clinical evidence / method / limitation
- **Why relevant**: ...
```

---

## 2. Evidence Chain Extraction

### Process

When the user provides a paragraph or claims:

1. **Identify key claims** in the text — extract each factual/conceptual statement.
2. **Generate search queries** for each claim.
3. **Search Zotero** for supporting and contrasting evidence.
4. **Match each claim** with relevant citations, noting whether the citation supports, contrasts with, or provides context for the claim.
5. **Flag gaps** — claims with no supporting literature in the library.

### Evidence Types

- **Direct support**: directly supports the claim.
- **Indirect support**: supports part of the mechanism or context.
- **Contrasting evidence**: reports inconsistent or opposite findings.
- **Mechanistic evidence**: explains biological, behavioral, or methodological mechanisms.
- **Methodological evidence**: supports the design, measurement, or analytical method.
- **Background evidence**: useful for introduction or broad framing.
- **Gap**: no adequate Zotero evidence found.

### Output Format

```markdown
## Evidence Chain

### Claim 1: [extracted claim text]

**Claim type**: causal / association / mechanism / background / method

**Evidence found**:
- ✅ Direct support: Author et al. (Year), Title, ItemKey, DOI
- 🧬 Mechanistic evidence: Author et al. (Year), Title, ItemKey, DOI
- 🔄 Contrasting evidence: Author et al. (Year), Title, ItemKey, DOI

**Assessment**:
- Evidence strength: strong / moderate / weak / insufficient
- Suggested wording: ...
- Citation gap: yes / no

### Claim 2: [extracted claim text]
- ⚠️ No direct evidence found in library
- Suggested search: [expanded query]

### Summary
- Claims with evidence: 3/5
- Claims needing new literature: 2
- Recommended DOI/PMID to search: ...
```

---

## 3. Citation-Grounded Writing Suggestions

### Process

When the user provides a manuscript paragraph:

1. **Analyze the paragraph** for: strength of claims, citation density, logical flow, terminology.
2. **Search Zotero** for relevant literature to support or strengthen each point.
3. Provide specific suggestions:

### Suggestion Types

| Type | Description |
|------|-------------|
| 🔗 **Add citation** | "This claim about X could be supported by [Author Year] in your library." |
| ✏️ **Reword claim** | "Your library shows mixed evidence for X; consider hedging with 'may' or 'suggests'." |
| 📊 **Add context** | "Your paper on [Topic Y] in your library provides context for this mechanism." |
| 🔄 **Replace citation** | "You cite [Old Ref], but [New Ref] in your library is more recent/relevant." |
| 🧩 **Identify gap** | "No literature in your library covers this point directly — consider searching for [query]." |
| 🏷️ **Terminology** | "Your library consistently uses [Term A] rather than [Term B] in similar contexts." |

### Output Format

```markdown
## Writing Suggestions

### Original Paragraph
> [user's text]

### Analysis
- **Key claims**: ...
- **Citation density**: X citations per sentence
- **Terminology check**: ...

### Suggestions
1. [Suggestion type] [specific suggestion]
2. [Suggestion type] [specific suggestion]
...

### Recommended Reads from Your Library
- [Paper 1] — relevant to [point]
- [Paper 2] — relevant to [point]
```

---

## 4. Strict Citation Verification

Use when the user asks to verify whether a specific claim, quote, or statistic is actually supported by the cited paper.

### Preflight

1. Estimate token budget: `Pages × 700 + 1000`
2. Warn if remaining tokens < 50k
3. Confirm full text is available in Zotero

### Verification Protocol

1. Extract complete PDF text to a temporary file
2. Read every page sequentially in 250-300 line chunks
3. Record exact line numbers for each claim, quote, and statistic
4. Cross-check numerical data (N=X, p<0.05, etc.) against the original
5. Compare claims against Zotero metadata and abstract

### Self-Audit Checklist

Before claiming "verification complete":
- [ ] Read complete text (first page → last page)
- [ ] Located References section (proves completeness)
- [ ] Recorded line numbers for all citations
- [ ] Verified numerical data (N=X, p<0.05)
- [ ] Checked author's evaluation wording
- [ ] Collected complete metadata from Zotero
- [ ] Stayed within token budget

### Output Format

```markdown
## Verification Report

| Claim | Paper | Line | Support level | Issue |
|-------|-------|------|---------------|-------|
| "X causes Y" | Author 2020 | 436 | Partial | supports association, not causation |
| "N=500" | Author 2021 | 152 | ✅ Correct | — |
```

---

## 5. Chinese Literature Verification

Use when the user needs to verify Chinese-language references (期刊论文、图书、学位论文、政策文件).

### Primary Method: CNKI CDP Direct Search

When Chrome MCP tools are available:

1. Navigate to `kns.cnki.net/kns8s/AdvSearch`
2. Check for CAPTCHA via screenshot (not snapshot text alone)
3. Enter exact title into the search field
4. Click search and wait for results
5. Extract structured data from the results table
6. Compare: title / authors / journal / year

**Verdicts**:
- **Confirmed**: exact title + author + journal + year all match
- **Likely Real**: title matches, 2 of 3 remaining fields match
- **Metadata Error**: paper exists but citation info is wrong
- **Not Found**: proceed to WebSearch fallback

### Fallback: Multi-Source WebSearch

When CDP is unavailable, execute ALL of the following:

1. `"<full title>"` (exact match)
2. `<title> <author>` (broader match)
3. `"<title>" site:cnki.net`
4. `"<title>" site:wanfangdata.com.cn`
5. `"<title>" site:xueshu.baidu.com`

### Rules for Chinese Literature

- Do NOT claim "Uncertain (needs CNKI verification)" as final verdict
- No DOI ≠ fabricated (most Chinese papers lack DOIs)
- Must give a definitive verdict: Confirmed / Likely Real / Likely Fabricated / Metadata Error

---

## 6. Chinese Academic Writing Rules

When responding in Chinese:

- Keep article titles, journal names, author names, DOI, PMID, and item keys in English.
- Do not translate official paper titles unless the user asks.
- Distinguish association, causation, mediation, prediction, and mechanism.
- Use cautious wording when evidence is indirect, observational, or inconsistent.
- Do not use a Zotero item as evidence unless its metadata, abstract, full text, note, or annotation has been inspected.
- Clearly mark whether each citation is for background, method, mechanism, or direct empirical evidence.
- When the evidence is insufficient, suggest hedging: "可能"、"提示"、"与…相关" rather than "证明"、"导致".

---

## 7. External Source Fallback

When Zotero returns insufficient results, recommend these free MCP Servers:

| Source | Covers | API Key | Best for |
|--------|--------|---------|----------|
| crossref-academic-mcp-server | Crossref + OpenAlex + Semantic Scholar | None | DOI lookup, citation graph, author profile |
| paper-search-mcp | arXiv + PubMed + bioRxiv | None | Preprints, biomedical literature |
| academix | OpenAlex + DBLP + Semantic Scholar + arXiv + CrossRef | None | CS/AI/ML papers, multi-source aggregation |

### Workflow

1. Search Zotero first
2. If insufficient, suggest external MCP tools
3. Mark all external results with source labels
4. Ask the user whether to add found papers to Zotero

---

## Usage Examples

### Search

> "帮我搜一下 Zotero 里关于肠道菌群与抑郁症的孟德尔随机化研究"

The skill will:
1. Expand to: `semantic_search("gut microbiota depression Mendelian randomization")` + `search_library(q="gut microbiota depression MR", tags=["Mendelian Randomization", "depression"])`
2. Return combined results with similarity scores and Zotero links

### Evidence Chain

> "以下是一段草稿，请帮我找证据链：
> '慢性炎症通过激活 JAK-STAT 信号通路促进动脉粥样硬化斑块形成，而 IL-6 受体阻断剂可显著降低心血管事件风险。'"

The skill will:
1. Extract claims: (a) chronic inflammation → JAK-STAT → atherosclerosis, (b) IL-6R blockade → reduced CVD risk
2. Search: "chronic inflammation JAK-STAT atherosclerosis", "IL-6 receptor inhibitor cardiovascular risk"
3. Match each claim to papers in library

### Strict Verification

> "请验证'IL-6 受体阻断剂可降低心血管事件风险'这句话，确认原文确实这么说了"

The skill will:
1. Extract claim: IL-6R blockade → reduced CVD risk
2. Find the cited paper in Zotero
3. Extract and read full PDF sequentially
4. Report exact line number and quote
5. Judge: fully supports / partially supports / does not support

### Writing Suggestions

> "帮我润色这段讨论，并补充合适的引用：
> '我们的研究发现某基因与 2 型糖尿病之间存在显著关联。这一结果与以往研究一致。'"

The skill will:
1. Search for relevant genetic association studies in library
2. Suggest specific citations for "以往研究"
3. Suggest more precise wording based on library terminology patterns
4. Recommend additional analyses from similar papers

---

## Notes

- Always prefer **semantic search** first for conceptual queries.
- For author/year specific lookups, use keyword search with exact fields.
- Zotero links use the format: `zotero://select/items/0_{ItemKey}`
- If the user has not built the semantic index yet, prompt them to run `zotero-mcp update-db`.
- If full-text is needed, suggest `zotero-mcp update-db --fulltext`.
- Token budget for full verification: estimate 700 tokens per page + 1000 overhead.
