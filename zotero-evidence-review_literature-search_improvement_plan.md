# zotero-evidence-review 文献检索场景改进方案

## 1. 背景问题

当前 `zotero-evidence-review` skill 已经能处理“给一段文本找证据、补引文、润色并导出证据包”的场景，但在“目标文献检索”场景中显得不够贴合。

典型表现：

| 问题 | 当前表现 | 影响 |
|---|---|---|
| 场景混杂 | 检索请求容易被导向 Evidence Package / 段落证据模板 | 输出过重，出现 Copy-ready text、Claim matrix 等不必要内容 |
| 输出模板过强 | 纯文献检索也套用 17 节 evidence report | 检索结果不够清爽，用户难以快速判断“哪些文献值得看” |
| RIS 导出逻辑偏写作证据包 | RIS 强绑定“推荐引用/稿件文本” | 对“专题检索 + 文献清单导出”不自然 |
| 检索结果分类不足 | 相关文献、核心文献、方法文献、噪音文献边界不够清晰 | 容易把疾病 GWAS、方法学 GWAS、脑影像 GWAS 混在一起 |
| 自动识别粒度不够 | 同一个 skill 同时想服务“文本补引用”和“目标文献检索” | 需要新增独立路由，避免互相干扰 |

本方案的核心目标是：保留并保护原有“段落补引文/润色”能力，同时新增一个轻量、检索优先、分类清晰、可导出 MD/RIS 的“目标文献检索场景”。

## 2. 目标场景拆分

建议将 skill 的用户请求明确分为两条主线：

### A. 段落证据与写作增强

适用请求：

- “帮我给这段话补引用”
- “润色这段讨论并给出参考文献”
- “这句话有没有证据支持”
- “根据文献改写这段话”

保持现有 Module 2 / Module 2.5 逻辑：

- Claim extraction
- Evidence level A-E
- Copy-ready Manuscript Text
- Annotated Recommended Text
- Citation Support Ledger
- Evidence Package
- RIS for recommended manuscript citations

### B. 目标文献检索与文献清单导出

新增场景，建议命名为：

`target_literature_search`

适用请求：

- “检索哪些文献使用了大脑相关 GWAS 数据”
- “帮我找 Zotero 里关于 X 的文献”
- “输出一个专题检索报告和 RIS”
- “筛选某方向核心文献”
- “找目标文献/相关文献/方法文献”
- “帮我导出这个主题下的文献清单”

新增输出重点：

- 检索策略
- 结果分层
- 纳入/排除标准
- 文献表
- 主题分类
- RIS 导出
- 后续阅读建议

不输出或弱化：

- Copy-ready Manuscript Text
- 段落 diff
- 逐句引文推荐
- Claim–Evidence Matrix 的复杂写作版

## 3. Intent Detection 改造建议

在原 skill 的 `0. Intent Detection` 表中新增一类：

```markdown
| `target_literature_search` | 用户请求是专题/目标文献检索、Zotero 库内文献发现、筛选哪些文献使用某数据/方法/表型/疾病、导出检索报告或 RIS，但没有提供需要补引文的段落 | **Module 1.8: Target Literature Search + Search Report Export** |
```

### 路由判定规则

建议优先级：

1. 如果用户提供了完整段落，并要求补引用、改写、润色、证据支持 → `paragraph/package`
2. 如果用户没有提供段落，而是要求“检索哪些文献/找目标文献/导出文献清单/RIS” → `target_literature_search`
3. 如果用户同时提供主题和“生成报告/RIS”，但没有稿件段落 → `target_literature_search_export`
4. 如果用户提供具体引用和具体 claim 要核实 → `verify`

### 防误判规则

新增规则应明确：

```markdown
如果用户问“哪些文献使用了 X 数据/方法/表型/队列/GWAS”，不要默认进入 Paragraph Citation Package Workflow，除非用户同时提供了需要改写或补引文的稿件段落。
```

## 4. 新增 Module 1.8：Target Literature Search

建议插入在 Module 1 之后，作为检索场景的专用模块。

### 4.1 输入识别

将用户问题拆成以下字段：

| 字段 | 示例 |
|---|---|
| Topic | 大脑相关 GWAS 数据 |
| Core concept | brain imaging-derived phenotypes; neuroimaging GWAS; cortical thickness; subcortical volume |
| Target relation | “哪些文献使用了这些数据” |
| Search scope | Zotero local library first; PubMed optional |
| Output request | chat table / MD report / RIS |
| Inclusion boundary | 使用脑影像/脑结构/脑细胞/脑相关 GWAS 数据 |
| Exclusion boundary | 纯疾病 GWAS、GWAS Catalog、通用方法学但未使用脑数据 |

### 4.2 检索流程

推荐流程：

```text
Zotero readiness smoke test
→ semantic search for broad recall
→ keyword searches for precise concepts
→ candidate pooling
→ deduplicate by DOI / title / Zotero key
→ classify candidates into Core / Related / Method / Exclude
→ inspect Zotero metadata for selected candidates
→ optional PubMed expansion
→ generate search report
→ generate RIS for selected Included records
```

### 4.3 检索查询生成

新增 query expansion 模板：

```markdown
用户问题：哪些文献使用了大脑相关 GWAS 数据？

Semantic query:
studies using brain-related GWAS data, brain imaging-derived phenotypes, neuroimaging GWAS,
cortical thickness, cortical surface area, subcortical brain volumes, basal ganglia GWAS,
MRI-derived brain phenotypes

Keyword queries:
- "brain imaging-derived phenotypes GWAS"
- "neuroimaging GWAS"
- "cortical thickness surface area GWAS"
- "subcortical brain morphometry GWAS"
- "basal ganglia GWAS"
- "brain MRI GWAS Mendelian randomization"
- "brain cell type GWAS eQTL"
```

## 5. 新增结果分类体系

文献检索场景不应只输出“相关/不相关”，而应输出“为什么属于这个主题”。

建议分类：

| 分类 | 定义 | RIS 默认动作 |
|---|---|---|
| Core | 直接使用目标数据/方法/表型，如 brain IDPs GWAS、cortical thickness GWAS | Include |
| Strong Related | 使用相邻脑相关遗传数据，如 brain cell eQTL + GWAS、NIDP TWAS | Include / Optional |
| Method Background | 方法学重要，但未直接使用目标主题数据 | Optional / Exclude |
| Disease GWAS Only | 只研究脑疾病/精神疾病 GWAS，但没有脑影像或脑结构数据 | Exclude |
| Noise | 检索误召回 | Exclude |
| Verify | 元数据或摘要不足，需要全文确认 | Verify |

建议在报告中加入：

```markdown
## 结果分类标准
| Category | Include rule | Exclude rule |
```

## 6. 新增轻量 Search Report 模板

建议新增一个独立模板，不复用完整 `EVIDENCE_REVIEW_REPORT`。

模板名：

`LITERATURE_SEARCH_REPORT`

建议结构：

```markdown
# 文献检索报告：{topic}

## 1. 检索任务
| Field | Value |
|---|---|
| Topic | ... |
| User question | ... |
| Search date | ... |
| Zotero status | Connected / Failed |
| PubMed status | Completed / Failed / Unavailable / Not executed |
| Output | MD report + RIS |

## 2. 纳入与排除标准
| Decision | Criteria |
|---|---|
| Include | ... |
| Exclude | ... |
| Verify | ... |

## 3. 核心发现
- 3-5 条中文总结

## 4. 检索结果总表
| # | Citation | Year | Category | Role | Zotero key | DOI/PMID | Why included | RIS action |

## 5. 分类结果
### Core
| Citation | Data / method used | Why core |

### Strong Related
| Citation | Relation | Why related |

### Excluded / Noise
| Citation | Reason |

## 6. 推荐阅读顺序
| Priority | Citation | Why read first |

## 7. Search Reproducibility
| Source | Query | Mode | Max results | Status | Hits | Included | Notes |

## 8. Metadata QC
| Citation | DOI | PMID | PDF | Missing metadata | Duplicate / mismatch | RIS action |

## 9. Export Files
- Markdown report: `...`
- RIS: `...`
```

### 与 Evidence Package 模板的区别

| Evidence Package | Literature Search Report |
|---|---|
| 面向稿件段落和引文放置 | 面向主题检索和文献筛选 |
| 有 Copy-ready Manuscript Text | 无需稿件文本，除非用户另行要求 |
| 有 Claim–Evidence Matrix | 有 Literature Classification Table |
| RIS 是稿件推荐引用 | RIS 是检索后纳入文献清单 |
| 适合写作增强 | 适合文献发现、选题、综述前期整理 |

## 7. RIS 导出规则改造

新增 `Search RIS` 概念，与原来的 `Citation RIS` 区分。

### Citation RIS

用于段落补引文：

- 只包含推荐用于稿件段落的引用
- 强依赖 Citation Support Ledger
- 排除不支持 claim 的文献

### Search RIS

用于目标文献检索：

- 包含 `Category = Core` 的文献
- 可按用户要求包含 `Strong Related`
- 默认排除 `Method Background`、`Disease GWAS Only` 和 `Noise`
- `Verify` 条目默认不纳入，除非用户要求“先全部导出”

建议在 skill 中写明：

```markdown
In target_literature_search mode, RIS represents the selected literature set, not manuscript citation placement. Do not require Copy-ready Manuscript Text or sentence-level citation recommendations before writing RIS.
```

## 8. 输出模式建议

文献检索场景可以支持三种输出模式：

| 模式 | 触发语 | 输出 |
|---|---|---|
| Chat Search | “找一下/哪些文献” | 聊天内表格 + Refs |
| Search Report | “生成报告/保存 MD” | MD 文档 |
| Search Report + RIS | “导出 RIS/EndNote/参考文献” | MD + RIS |

自动识别规则：

```markdown
如果用户说“导出 MD / 报告 / RIS / EndNote”，走 Search Report + RIS。
如果用户只说“检索一下”，默认 Chat Search，不生成文件，除非用户要求。
```

这样可以避免每次普通检索都生成重文件。

## 9. 推荐的 SKILL.md 最小改动清单

建议不要重写整个 skill，只做最小增量修改：

1. 在 Intent Detection 表中新增 `target_literature_search`
2. 在 Routing Rules 中加入“不带段落的主题检索不进入 Paragraph Citation Package Workflow”
3. 在 Module 1 后新增 `Module 1.8 Target Literature Search`
4. 在 Appendix 中新增 `LITERATURE_SEARCH_REPORT` 模板
5. 在 RIS 规则中区分 `Citation RIS` 与 `Search RIS`
6. 在 final chat 输出中新增 Search Report 输出格式

## 10. 建议插入文本草案

### 10.1 Intent Detection 新增行

```markdown
| `target_literature_search` | Topic/question asks which papers use a data source, method, phenotype, cohort, disease area, or research direction; user wants literature discovery, screening, search report, MD, RIS, or EndNote export, and no manuscript paragraph is supplied | **Module 1.8: Target Literature Search and Export** |
```

### 10.2 Routing Rule 新增

```markdown
Target literature search separation:
If the user asks "which papers use X", "find papers about X", "search Zotero for X", "export a literature list/report/RIS", or equivalent, and does not provide a manuscript paragraph to revise, route to `target_literature_search`, not the Paragraph Citation Package Workflow. This mode may write a Markdown search report and RIS, but it must not require Copy-ready Manuscript Text, sentence-level citation placement, or paragraph diff output.
```

### 10.3 Module 1.8 开头草案

```markdown
## 1.8 Target Literature Search and Export

Use this module when the user wants to discover, screen, classify, or export papers around a topic, method, dataset, phenotype, cohort, disease area, or question, without asking to revise a manuscript paragraph.

Core output is a literature search report, not a paragraph evidence package.
```

## 11. 对当前“大脑相关 GWAS”案例的理想输出

如果新增场景生效，用户请求：

> 哪些文献使用了大脑相关 GWAS 数据？导出 MD 和 RIS。

理想流程应是：

```text
smoke test Zotero
→ semantic query: brain-related GWAS / IDPs / neuroimaging GWAS
→ keyword query: brain imaging-derived phenotypes GWAS
→ keyword query: cortical thickness surface area GWAS
→ keyword query: subcortical brain morphometry GWAS
→ classify:
   Core: Lin 2023, Bahrami 2024, Tissink 2024...
   Strong Related: Hao 2024, Wang 2026...
   Exclude: GWAS Catalog, pure disease GWAS...
→ write LITERATURE_SEARCH_REPORT
→ write Search RIS
```

理想最终回复：

```markdown
Generated Literature Search Package:
- Status: Caution
- Markdown report: `zotero-evidence-output/..._literature_search.md`
- EndNote RIS: `zotero-evidence-output/..._references.ris`
- Included records: 15
- Critical warnings:
  - PubMed expansion failed; Zotero-only package.
```

## 12. 实施计划

### Phase 1：轻量改造

- 增加 `target_literature_search` intent
- 新增 `LITERATURE_SEARCH_REPORT` 模板
- 区分 `Search RIS` 与 `Citation RIS`
- 更新 final chat 格式

预计改动范围：`SKILL.md` 内 4-6 个小节。

### Phase 2：检索质量增强

- 增加 topic decomposition 规则
- 增加 Core / Related / Exclude 分类标准
- 增加 query expansion examples
- 增加“噪音文献排除原因”表

### Phase 3：可选脚本化

若后续经常导出检索报告，可新增脚本：

```text
scripts/write_literature_search_package.py
```

脚本职责：

- 输入 JSON/YAML 文献候选
- 输出标准 MD report
- 输出 RIS
- 校验 RIS 起止标签

但第一阶段不建议马上脚本化，先验证模板和路由是否符合真实使用。

## 13. 验收标准

改造完成后，应满足：

| 测试请求 | 预期路由 |
|---|---|
| “帮我给这段话补引用并润色：...” | paragraph / package |
| “哪些文献使用了大脑相关 GWAS 数据？” | target_literature_search |
| “检索 Zotero 中关于肠道菌群和抑郁症的文献” | target_literature_search 或 chat search |
| “导出关于 IL-6 MR 的文献 MD 和 RIS” | target_literature_search_export |
| “验证这篇文献是否支持这句话” | verify |

通过标准：

- 纯文献检索不再输出 Copy-ready Manuscript Text / diff paragraph
- 段落补引文不受影响，仍使用现有 Evidence Package
- RIS 能按场景区分：检索清单 vs 稿件推荐引用
- 报告中有清晰的纳入、排除、分类和检索复现记录

## 14. 推荐结论

不建议把现有 `zotero-evidence-review` 完全重写。更稳妥的方式是新增 `target_literature_search` 分支，使 skill 形成双核心：

1. **Paragraph Evidence Workflow**：服务“段落补引文 + 润色 + 证据包”
2. **Target Literature Search Workflow**：服务“专题检索 + 文献分类 + MD/RIS 导出”

这样既保留现有强项，又能让“文献检索”输出变轻、变准、变符合用户预期。
