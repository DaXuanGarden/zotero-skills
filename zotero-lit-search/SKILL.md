---
name: zotero-lit-search
description: Search Zotero library via semantic/concept matching, convert natural language into structured queries, extract evidence-chain citations from a paragraph, and provide writing suggestions grounded in the user's Zotero collection. Requires Zotero MCP to be configured.
license: MIT
compatibility: opencode
metadata:
  workflow: academic-research
  requires: zotero-mcp
---

# Zotero Literature Search Skill

## Overview

Use Zotero MCP tools to search the user's Zotero library intelligently. This skill combines **semantic search** (concept matching via embeddings) with **keyword/structured search**, helps **build evidence chains** from draft text, and provides **citation-grounded writing suggestions**.

---

## 1. Semantic + Structured Search

### Process

1. If the user asks in natural language, first expand their query into structured search terms.
2. Run **semantic search** first (concept matching, finds conceptually related papers even without keyword overlap).
3. If results are insufficient, fall back to **keyword search** with relevant filters (tags, authors, year range, item type).
4. Present results with: title, authors, year, journal, similarity score (for semantic), tags, and a Zotero direct link.

### Query Expansion Examples

| User says | Expanded structured query |
|-----------|--------------------------|
| "气候变化 心血管疾病 风险" | `q: "climate change cardiovascular disease risk", semantic: true, tags: ["cardiovascular"], year: 2020-2026` |
| "孟德尔随机化 药物靶点 2型糖尿病" | `q: "Mendelian randomization drug targets type 2 diabetes", semantic: true, tags: ["MR", "drug targets"], itemType: "journalArticle"` |
| "肠道菌群 抑郁症 机制" | `q: "gut microbiota depression mechanism", semantic: true, year: 2020-2026` |

---

## 2. Evidence Chain Extraction

### Process

When the user provides a paragraph or claims:

1. **Identify key claims** in the text — extract each factual/conceptual statement.
2. **Generate search queries** for each claim.
3. **Search Zotero** for supporting and contrasting evidence.
4. **Match each claim** with relevant citations, noting whether the citation supports, contrasts with, or provides context for the claim.
5. **Flag gaps** — claims with no supporting literature in the library.

### Output Format

```markdown
## Evidence Chain

### Claim 1: [extracted claim text]
- ✅ Supporting: Author (Year) — "Title" — [zotero link]
- 🔄 Contrasting: Author (Year) — "Title" — [zotero link]
- 📝 Context: Author (Year) — "Title" — [zotero link]

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
