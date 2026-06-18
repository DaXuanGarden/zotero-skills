# Zotero Evidence Review 输出改进开发计划

> 目标：将当前“Zotero 检索结果报告”升级为面向科研写作的 **Evidence Package**：每次检索后只输出两个核心文件——一个可读、可追溯的 Markdown 报告，以及一个可直接导入 EndNote 的参考文献文件。

## 1. 产品目标

当前 Zotero 检索结果已经能够给出候选文献、主张-证据矩阵和写作建议，但仍存在以下问题：

1. 结果主要停留在聊天窗口中，缺少可保存、可复用的文件化输出。
2. Zotero item key（如 `KYX3784V`）直接暴露在正文中，对科研写作者价值有限。
3. Zotero 链接未被包装为可读的超链接，跳转体验较差。
4. 检索到的文献无法直接进入 EndNote / Word 写作工作流。
5. 写作建议主要基于 Zotero 本地库，尚未系统整合 PubMed 扩展检索结果。
6. 报告更像“检索结果列表”，还没有形成“证据审查 + 引文决策 + 写作建议”的完整产品形态。

因此，本功能的核心目标是：

> 围绕用户输入的段落、论断或写作问题，自动完成 Zotero 本地检索与 PubMed 扩展检索，生成一个可追溯的 Markdown 证据报告，并同步生成一个可直接导入 EndNote 的参考文献文件，帮助用户完成论文写作中的证据判断、引文布置和引用管理。

---

## 2. 最终输出文件设计

为保持工作流简洁，每次检索后默认只生成两个文件：

```text
YYYY-MM-DD_{topic_slug}_evidence_review.md
YYYY-MM-DD_{topic_slug}_references.ris
```

其中：

| 文件 | 用途 | 要求 |
|---|---|---|
| `YYYY-MM-DD_{topic_slug}_evidence_review.md` | 人读的证据报告 | 包含 Zotero 检索、PubMed 扩展、主张-证据矩阵、写作改进建议、可点击链接 |
| `YYYY-MM-DD_{topic_slug}_references.ris` | EndNote 导入文件 | 元数据必须与 Zotero 中检索到的文献保持一致，确保 Word / EndNote 引用准确 |

### 2.1 为什么优先使用 RIS 而不是 EndNote XML

EndNote 可以稳定导入 RIS 文件，且 RIS 字段结构清晰，便于从 Zotero 元数据中直接生成。相比之下，EndNote XML 字段层级复杂，如果手写 XML，容易产生兼容性问题。

因此第一阶段建议采用：

```text
references.ris 作为默认 EndNote 导入格式
```

后续如果能够直接调用 Zotero translator 或 Better BibTeX / Zotero export translator，再增加：

```text
references.endnote.xml 作为可选增强格式
```

但默认交付文件仍保持两个：

```text
1. Markdown report
2. RIS reference file
```

---

## 3. 元数据一致性要求

EndNote 文件中的参考文献元数据必须优先来自 Zotero，而不是由模型根据记忆或摘要自行生成。

### 3.1 元数据来源优先级

生成 RIS 时，字段来源按以下优先级：

1. Zotero item metadata。
2. Zotero DOI / PMID / ISBN 等唯一标识符。
3. PubMed 返回的标准元数据，仅用于 Zotero 中不存在或缺失字段的外部扩展文献。
4. 模型不得凭空补全作者、期刊、卷期页码、DOI。

### 3.2 Zotero 文献的字段映射

| Zotero 字段 | RIS 字段 | 说明 |
|---|---|---|
| itemType | TY | journalArticle -> JOUR；book -> BOOK；conferencePaper -> CONF；preprint -> UNPB（已期刊收录时可用 JOUR）；report -> RPRT；thesis -> THES；webpage -> ELEC；bookSection -> CHAP；dataset -> DATA；patent -> PAT |
| creators | AU | 每位作者单独一行 `AU  - Last, First` |
| date | PY / Y1 | 年份与完整日期 |
| title | TI | 文献标题 |
| publicationTitle | JO / T2 | 期刊名 |
| journalAbbreviation | J2 | 期刊缩写，如有 |
| volume | VL | 卷 |
| issue | IS | 期 |
| pages | SP / EP | 起止页；无法拆分时可写入 SP 或 `EP` 留空 |
| DOI | DO | DOI |
| PMID | AN 或 N1 | PMID 可写入 accession number 或 note |
| url | UR | URL |
| abstractNote | AB | 摘要，如需要 |
| language | LA | 语言 |
| tags | KW | 每个 tag 一行 |
| item key | N1 | 可选，记录 `Zotero key: XXXXXXXX`，但不作为正文展示 |

### 3.3 RIS 生成原则

每条文献必须以 `TY` 开始，以 `ER  -` 结束，例如：

```ris
TY  - JOUR
AU  - Moran, Lisa J.
PY  - 2013
TI  - The contribution of diet, physical activity and sedentary behaviour to body mass index in women with and without polycystic ovary syndrome
JO  - Human Reproduction
VL  - 28
IS  - 8
SP  - 2276
EP  - 2283
DO  - 10.1093/humrep/det256
N1  - Zotero key: GD6Q3CC9
ER  -
```

注意：

- 作者不得由模型猜测。
- DOI 必须与 Zotero 元数据一致。
- 如果 Zotero 与 PubMed 元数据冲突，应在 Markdown 报告中提示“metadata mismatch”，默认以 Zotero 为准。
- 如果 Zotero 元数据不完整，应在报告中列出缺失字段，避免生成错误引用。

---

## 4. Markdown 报告结构

Markdown 报告应成为科研写作者的主界面，而不是简单的检索日志。

推荐结构如下：

```markdown
# Evidence Review: {topic}

Generated: {date}
Source: Zotero local library; PubMed: {Completed / ⚠️ Tool unavailable; search not executed / Failed; query reported / Not executed only for explicit chat-only or non-PubMed workflows}
Input: {user paragraph or claim}

## 1. Bottom Line
## 2. Recommended Manuscript Text
## 3. Claim–Evidence Matrix
## 4. Citation Placement
## 5. Reference Table
## 6. Zotero Search Summary
## 7. PubMed Expansion
## 8. Integrated Writing Advice
## 9. Gaps and Reviewer-risk Assessment
## 10. Metadata Quality Control
## 11. Export File
```

---

## 5. 文献表设计

报告中不应直接显示一堆 Zotero item key。item key 应隐藏在超链接或备注中。

推荐表格：

```markdown
| # | Citation | Year | Study type | Main use | Zotero | PDF | DOI | PMID | Collection |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Kazemi et al., *Human Reproduction Update* | 2022 | Systematic review / meta-analysis | Supports heterogeneity of lifestyle evidence in PCOS | [Item](zotero://select/items/0_KYX3784V) | [PDF](zotero://open-pdf/library/items/{attachment_key}) | [DOI](https://doi.org/10.1093/humupd/dmac023) | [PMID](https://pubmed.ncbi.nlm.nih.gov/{pmid}/) | PCOS / Lifestyle |
```

### 5.1 链接规则

| 链接 | 格式 | 说明 |
|---|---|---|
| Zotero item | `[Item](zotero://select/items/0_{item_key})` | 跳转到 Zotero 条目 |
| Zotero PDF | `[PDF](zotero://open-pdf/library/items/{attachment_key})` | 直接打开 PDF 附件 |
| DOI | `[DOI](https://doi.org/{doi})` | 跳转到 DOI 页面 |
| PubMed | `[PMID](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)` | 跳转 PubMed |

如果没有附件，则 PDF 列显示：

```markdown
—
```

如果无法确认所在 collection，则 Collection 列显示：

```markdown
Not available
```

---

## 6. Zotero 检索模块

Markdown 报告应记录本地 Zotero 检索过程，包括：

1. 语义检索结果。
2. 关键词检索结果。
3. 去重后的最终纳入文献。
4. 因相关性不足而排除的文献，如有需要。
5. 本地库中的证据缺口。

建议格式：

```markdown
## Zotero Search Summary

| Search route | Query | Hits | Included | Notes |
|---|---|---:|---:|---|
| Semantic search | sedentary behavior PCOS epidemiology | 12 | 5 | Retrieved lifestyle and PCOS studies |
| Keyword search | "sedentary behavior" "polycystic ovary syndrome" | 4 | 3 | More specific but fewer results |
| Genetic background search | PCOS GWAS genetic correlation | 8 | 3 | Supports PCOS genetic architecture, not sedentary-PCOS shared genetics directly |
```

---

## 7. PubMed 扩展检索模块

完成 Zotero 检索后，应自动到 PubMed 扩展检索。PubMed 结果用于：

1. 发现 Zotero 本地库缺失的重要文献。
2. 验证 Zotero 检索是否遗漏关键研究。
3. 为最终写作建议提供外部证据背景。
4. 标注哪些文献已在 Zotero 中，哪些尚未导入。

### 7.1 PubMed 检索式记录

报告中必须记录 PubMed 检索式，例如：

```markdown
## PubMed Expansion

Date: 2026-06-18
Database: PubMed
Status: Completed / ⚠️ Tool unavailable; search not executed / Failed; query reported

Query:

```text
("polycystic ovary syndrome"[Title/Abstract] OR PCOS[Title/Abstract])
AND
("sedentary behavior"[Title/Abstract] OR "sedentary time"[Title/Abstract] OR "physical activity"[Title/Abstract])
AND
(cohort[Title/Abstract] OR longitudinal[Title/Abstract] OR "case-control"[Title/Abstract] OR cross-sectional[Title/Abstract])
```
```

### 7.2 PubMed 结果表

```markdown
| # | Citation | PMID | DOI | In Zotero? | Evidence use | Recommendation |
|---|---|---|---|---|---|---|
| 1 | Tay et al., 2020 | [PMID](https://pubmed.ncbi.nlm.nih.gov/{pmid}/) | [DOI](https://doi.org/10.1111/cen.14205) | Yes | PCOS, PA and sedentary behavior | Use as supporting citation |
| 2 | New Author et al., 2024 | [PMID](https://pubmed.ncbi.nlm.nih.gov/{pmid}/) | ... | No | Potentially relevant cohort evidence | Consider importing to Zotero / EndNote |
```

### 7.3 Zotero 与 PubMed 匹配规则

判断 PubMed 文献是否已在 Zotero 中，优先使用：

1. DOI 精确匹配。
2. PMID 精确匹配。
3. 标题规范化后匹配。
4. 作者 + 年份 + 期刊的模糊匹配。

如果存在疑似匹配但 DOI 不一致，应在报告中标注：

```markdown
Possible metadata mismatch: check DOI/title before citing.
```

---

## 8. 写作改进建议必须整合 Zotero + PubMed

最终写作建议不能只基于 Zotero 本地结果。必须综合：

1. Zotero 本地库中已检索到的证据。
2. PubMed 扩展检索发现的新证据。
3. Zotero 与 PubMed 的一致性或冲突。
4. 本地库缺失但 PubMed 提示存在的关键研究。
5. 证据强度、研究类型和审稿风险。

### 8.1 写作建议模块

推荐格式：

```markdown
## Integrated Writing Advice

### Original claim
{user's original sentence or paragraph}

### Evidence from Zotero
- Zotero local library supports ...
- Zotero local library does not support ...

### Evidence from PubMed
- PubMed expansion confirms ...
- PubMed expansion identifies additional studies suggesting ...
- PubMed expansion does not identify direct evidence for ...

### Recommended revision
> {rewritten paragraph}

### Why this wording is safer
{explain why the revised wording better matches the combined evidence base}
```

### 8.2 写作建议原则

- 如果 Zotero 支持某主张，但 PubMed 检索显示外部证据更复杂，应弱化措辞。
- 如果 Zotero 未找到证据，但 PubMed 找到高质量证据，应明确提示“本地库缺失，建议导入”。
- 如果 Zotero 与 PubMed 均未找到直接证据，应将主张标为 gap，不应强行推荐引用。
- 如果主张主要来自用户自己的研究结果，应明确写为“observed in our study”，并仅用外部文献支撑背景，而不是替代用户研究结果。

---

## 9. 主张-证据矩阵设计

推荐格式：

```markdown
## Claim–Evidence Matrix

| # | Claim | Zotero evidence | PubMed evidence | Evidence status | Confidence | Caveat | Recommended citation |
|---|---|---|---|---|---|---|---|
| 1 | Prior epidemiological studies are heterogeneous | Supported by local systematic review and observational studies | PubMed confirms heterogeneous study designs and exposure definitions | Supported | Moderate–high | Sedentary behavior and physical activity are not always measured separately | Kazemi 2022; Moran 2013; Tay 2020 |
| 2 | Cohort studies support sedentary behavior as a risk factor for incident PCOS | Limited | PubMed search needed / mixed / insufficient | Gap or partly supported | Low–moderate | Available studies may focus on weight gain or PCOS-related traits rather than incident PCOS | Use cautious wording |
```

---

## 9. Reviewer-risk Assessment

报告应从审稿人角度提示潜在风险。

```markdown
## Gaps and Reviewer-risk Assessment

| Affected claim / sentence | Risk | Severity | Evidence basis | Suggested fix |
|---|---|---|---|---|
| Cohort studies support sedentary behavior as a risk factor for incident PCOS | Overstating cohort evidence | High | Zotero and PubMed do not clearly identify direct prospective evidence for sedentary behavior -> incident PCOS | Replace with “population-based and longitudinal evidence suggests associations...” |
| Sedentary behavior and physical activity are interchangeable | Mixing sedentary behavior and physical activity | Moderate | Many studies assess PA rather than sedentary behavior specifically | Use “sedentary behavior, physical activity, and related lifestyle factors” |
| Shared genetics explain sedentary behavior and PCOS | Genetic interpretation overreach | High | Prior literature supports PCOS genetics but not necessarily shared genetic architecture with sedentary behavior | Attribute shared genetic architecture primarily to the current study |
```

---

## 10. Metadata Quality Control

质控结果应在导出文件信息之前展示，因为缺失元数据、冲突和重复项会直接影响引用可信度与 RIS 导入质量。

```markdown
## Metadata Quality Control

| Citation | Missing metadata | Metadata mismatch | Duplicate warning | RIS action |
|---|---|---|---|---|
| Author Year | DOI / PMID / pages / none | Possible metadata mismatch / none | Possible duplicate / none | Include / exclude / needs manual check |
```

---

## 11. EndNote 导入文件内容要求

`{topic_slug}_references.ris` 应包含：

1. 报告中最终推荐引用的 Zotero 文献。
2. PubMed 扩展检索中被标记为“建议引用”或“建议导入”的文献。
3. 不应包含所有低相关性检索命中文献。
4. 每条记录都应尽量保留 DOI、PMID、期刊、卷期页码等完整元数据。

### 11.1 文献纳入标准

RIS 中默认纳入：

| 文献类型 | 是否纳入 RIS | 说明 |
|---|---|---|
| Zotero 中用于最终推荐段落的文献 | 是 | 必须纳入 |
| Zotero 中仅作为背景但未推荐引用的文献 | 可选 | 视报告设置 |
| PubMed 中发现且建议补充引用的文献 | 是 | 元数据来自 PubMed，并在报告中标注“不在 Zotero” |
| PubMed 中低相关性文献 | 否 | 只在报告中简要记录或省略 |
| 元数据冲突未解决的文献 | 否或标记后纳入 | 默认不纳入，避免错误引用 |

### 11.2 RIS 文件顶部不添加 Markdown 注释

RIS 文件必须是纯 RIS 格式，不应加入 Markdown 标题、说明文字或代码块标记。

错误示例：

```text
# References
TY  - JOUR
...
```

正确示例：

```text
TY  - JOUR
AU  - Moran, Lisa J.
PY  - 2013
TI  - ...
ER  -
```

---

## 12. 用户体验流程

推荐交互流程：

```text
用户输入段落 / 论断
        ↓
解析核心概念与待验证主张
        ↓
Zotero 语义检索 + 关键词检索
        ↓
提取 Zotero 元数据、附件、collection、DOI、PMID
        ↓
PubMed 自动扩展检索
        ↓
DOI / PMID / 标题匹配 Zotero 与 PubMed
        ↓
构建主张-证据矩阵
        ↓
生成综合写作建议
        ↓
输出两个文件：
  1. evidence_review.md
  2. references.ris
```

---

## 13. 开发优先级

### P0：基础可用版本

1. 自动保存 Markdown 报告。
2. 报告中 Reference Table 表格化。
3. 隐藏 Zotero item key，只保留为超链接目标。
4. DOI、Zotero item、PDF 做成可点击链接。
5. 从 Zotero 元数据生成可导入 EndNote 的 RIS 文件。
6. 最终输出只展示两个文件路径。

### P1：证据质量增强

1. 添加 PubMed 自动扩展检索。
2. 根据 DOI / PMID 判断 PubMed 文献是否已在 Zotero。
3. 将 PubMed 结果纳入 Claim–Evidence Matrix。
4. 写作建议基于 Zotero + PubMed 综合证据生成。
5. 增加 reviewer-risk assessment。

### P2：元数据质量控制

1. 检测 Zotero 与 PubMed 元数据冲突。
2. 报告中列出缺失 DOI、缺失页码、缺失期刊等问题。
3. 对 RIS 导出前的关键字段进行校验。
4. 对疑似重复文献进行提示。

### P3：增强导出

1. 在能够稳定调用 Zotero translator 时，增加 EndNote XML 可选导出。
2. 增加 BibTeX 可选导出。
3. 增加 Word 引文布置清单。

---

## 14. 验收标准

### 14.1 Markdown 报告验收

- [ ] 报告自动保存为 `.md` 文件。
- [ ] 报告包含 Zotero 检索摘要。
- [ ] 报告包含 PubMed 扩展检索摘要。
- [ ] 报告包含主张-证据矩阵。
- [ ] 报告包含最终写作建议。
- [ ] 写作建议明确综合 Zotero 与 PubMed 证据。
- [ ] 文献表中 Zotero item key 不作为主要阅读对象出现。
- [ ] Zotero、PDF、DOI、PubMed 均尽量以超链接形式呈现。

### 14.2 RIS 文件验收

- [ ] RIS 文件可被 EndNote 成功导入。
- [ ] RIS 文件不包含 Markdown 或说明性文本。
- [ ] 每条记录均以 `TY  -` 开始，以 `ER  -` 结束。
- [ ] Zotero 文献的作者、标题、期刊、年份、卷期页码、DOI 与 Zotero 元数据一致。
- [ ] PubMed 补充文献的 DOI / PMID 与 PubMed 结果一致。
- [ ] 元数据冲突或缺失的文献不会被无提示地写入 RIS。

---

## 15. 推荐默认文件命名

根据主题和日期自动生成：

```text
2026-06-18_sedentary-behavior_pcos_evidence_review.md
2026-06-18_sedentary-behavior_pcos_references.ris
```

如果同一主题重复运行，可追加序号：

```text
2026-06-18_sedentary-behavior_pcos_evidence_review_v2.md
2026-06-18_sedentary-behavior_pcos_references_v2.ris
```

---

## 16. 总结

本次改进的核心不是把 Zotero 检索结果“展示得更好看”，而是把它变成一个真正服务科研写作的证据工作流：

1. Zotero 提供本地已管理文献和准确元数据。
2. PubMed 提供外部扩展和缺口检查。
3. Markdown 报告提供证据判断、写作建议和可追溯记录。
4. RIS 文件打通 EndNote / Word 引文工作流。

最终用户只需要两个文件：

```text
1. evidence_review.md       # 看证据、改写作、查链接
2. references.ris           # 导入 EndNote，进入 Word 引文流程
```

这将使 Zotero evidence review 从“检索辅助”升级为“论文写作证据引擎”。
