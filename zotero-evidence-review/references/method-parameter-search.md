# Methodology Parameter Extraction

Use this reference for Module 1.2 when the user asks what parameters a method or software uses, how an analysis selected or adjusted them, or where a paper reports the setting. Typical triggers include `方法学参数`, `软件参数`, `阈值`, `默认值`, `参数怎么调`, `GSMR 参数`, and `原文方法段落`.

The deliverable is a source-grounded parameter report, not a general paper list. Every parameter value and adjustment claim must be tied to inspected full text. Follow the global Zotero readiness, sequential-execution, PubMed, metadata, and RIS rules in `SKILL.md`.

## Search and Inspection

1. **Define the scope.** Record the method/software name and version if supplied, requested parameter names, analysis context, and whether the user wants original-method settings, software defaults, author recommendations, applied-study settings, or adjustment guidance. For broad requests, search for parameter families first; do not invent a complete parameter inventory.
2. **Search Zotero first.** Use short keyword queries for the method acronym/full name, canonical method-paper title or author, software/package name, and parameter labels. Use semantic search for broad recall, not as proof of an exact setting. Zotero metadata and abstracts identify candidate records but do not establish what a PDF's Methods section says.
3. **Classify the source role.** Use one or more of these labels for every value:
   - `Original method`: the paper introducing or formally describing the method.
   - `Software implementation`: package documentation, manual, or implementation paper describing available arguments and defaults.
   - `Author recommendation`: an explicit value or selection procedure recommended by the method/software authors.
   - `Applied-study choice`: a value selected by a later analysis.
   These roles are distinct. An applied-study value is not a software default. For Module 1.2, a source is `Core` when it directly defines, recommends, or tests a requested parameter, even if it is a methods paper rather than an application in the user's target disease.
4. **Use the global dual-MCP order.** Complete the Zotero smoke test and search first. For biomedical topics, attempt PubMed expansion afterward when a PubMed MCP tool is visible. PubMed metadata/abstracts can identify source papers but cannot stand in for an inspected Methods passage. A PubMed-only record must be labeled as such and must not receive a Zotero link unless its Zotero record is actually found.
5. **Inspect selected Zotero records sequentially.** Retrieve metadata, then child attachments to identify the actual main-PDF and supplement keys. Use the PDF outline to find `Methods`, `Statistical analysis`, `Methodological details`, `Software`, `Implementation`, or `Supplementary Methods`; read the relevant pages with `zotero_read_pdf_pages`. If the section or page cannot be found from the outline or extracted text, use full-text extraction on the selected source needed for the request, locate parameter terms, and confirm the passage by reading the PDF pages. Do not pre-schedule dependent Zotero calls before inspecting returned item/attachment keys.
6. **Capture one evidence unit per parameter or coherent parameter group.** Preserve exact parameter spelling, value, units, comparator, software version, and qualifying conditions. Keep a threshold and the rationale or selection rule together when the source reports them together. Inspect supplements if the main text points there.

## Interpreting Adjustment Advice

- Report separately what the original paper used, what documentation calls a default, what the authors recommend, and what application studies selected.
- Explain how changing a value affects results only when the inspected source states or tests that relationship. Mark further explanation as interpretation, not source evidence.
- If papers compare settings or run sensitivity analyses, give the tested range, selection criterion, and observed consequence. Do not turn one study's sensitivity range into a universal acceptable range.
- If no source explains how to tune a parameter, say so. A proposed sensitivity analysis may be listed as an analysis option, but not as a validated recommendation.
- When sources disagree, show settings side by side with source role, software version, population, and analysis context. Do not average values or silently select one.

## Passage and Zotero Location

For each included parameter, reproduce the complete relevant Methods paragraph in its original language when available. Preserve the source wording and notation; put translation and interpretation in separate fields. Include enough context to show what the setting controls. Do not silently repair OCR or infer missing text. Mark unreadable material as `[OCR 不清]` and report truncation or extraction failure.

Record the exact section/subsection and whether the passage is in the main text or a supplement. Give both printed page and physical PDF page when identifiable. The physical PDF page is the 1-indexed page used by `zotero_read_pdf_pages`; use it for the page jump. If printed pagination is absent or ambiguous, write `未标注`, not a guessed value.

Use these Zotero links only with keys obtained from inspected search/attachment results:

- Item: `[Zotero 条目](zotero://select/items/0_{parent_item_key})`
- PDF page: `[PDF 第{pdf_page}页](zotero://open-pdf/library/items/{attachment_key}?page={pdf_page})`
- PDF without a verified page target: `[PDF](zotero://open-pdf/library/items/{attachment_key})`

Never infer item or attachment keys. If the attachment is unavailable, give the item link, verified section/page information, and `PDF 页链接：不可用`. If a page-specific URI cannot be formed from a verified attachment key and physical page, provide the base PDF link and state that it opens without a page anchor.

## `METHOD_PARAMETER_EVIDENCE` Report Block

For saved reports, keep all required `LITERATURE_SEARCH_REPORT` sections and place this block under `## 8. 分类结果`, after the `Method Background` subsection. The normal search package path and Search RIS rules still apply. Use the same evidence table in chat-only mode, without creating files. Keep full metadata in the report's existing reference table/Refs block; cite sources elsewhere as `Author Year (KEY)`.

```markdown
### 方法学参数与原文定位（Module 1.2 only）
| 参数 | 原文设定 | 来源角色 | 用途/调整证据 | 方法学小节 | 印刷页 / PDF页 | Zotero PDF |
|---|---|---|---|---|---|---|
| {parameter} | {exact setting, units, conditions} | Original method / Software implementation / Author recommendation / Applied-study choice | {source-supported effect or 未报告} | {section/subsection} | {printed page / physical PDF page} | [PDF 第{N}页](zotero://open-pdf/library/items/{attachment_key}?page={N}) |

#### 原文定位段落
##### {Author Year — source role}
条目：[Zotero 条目](zotero://select/items/0_{parent_item_key})
位置：{main text or supplement; section/subsection; printed page; physical PDF page}
参数：{parameter names}

> {Complete relevant Methods paragraph verbatim}

解释/调整边界：{source-supported interpretation; distinguish analyst interpretation}
PDF 定位：[打开 PDF 第{N}页](zotero://open-pdf/library/items/{attachment_key}?page={N})

## 参数如何调整
| 目标/情形 | 可比较的设置 | 来源与证据 | 适用边界 |
|---|---|---|---|
| {...} | {...} | {source-linked comparison or 文献未提供可验证的调整依据} | {...} |
```

## Completion Check

- Every reported value is supported by inspected full text, not only a search result or abstract.
- Every passage names its source role, section, page information, Zotero item link, and PDF page link or a concrete unavailable reason.
- The page jump uses the verified physical PDF page; printed pagination is reported separately.
- Defaults, recommendations, original-method settings, and application-study choices remain distinct.
- Adjustment advice is source-supported or clearly labeled as interpretation/analysis option.
- Search, full-text, and attachment failures are reported as limitations, never as evidence that a parameter is absent.
- RIS includes only selected records whose metadata passed the repository's normal quality gates; PubMed-only records follow the global PubMed completion rule.
