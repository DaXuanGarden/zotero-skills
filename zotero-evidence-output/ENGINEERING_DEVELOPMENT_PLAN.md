# Zotero Evidence Output 工程化开发计划

生成日期：2026-06-19  
适用项目：`zotero-evidence-output` 证据审查报告生成与管理流程  
目标用户：科研工作者、论文作者、文献管理用户、AI-assisted evidence review 工具开发者

---

## 1. 项目目标

当前 `zotero-evidence-output/` 已经能够输出较完整的证据审查报告，包括 Bottom Line、Recommended Manuscript Text、Claim–Evidence Matrix、Reference Table、PubMed Expansion、Metadata QC 和 Reviewer-risk Assessment 等内容。

但目前输出仍然偏向“一次次独立生成的长报告”，缺少工程化组织、版本关系、全局索引、统一模板、引用去重和机器可读结构。

本开发计划的目标是将现有输出体系升级为一个更稳定、可复用、可审计、可扩展的科研证据管理系统。

核心改造方向：

1. 为 `zotero-evidence-output/` 建立项目级总览。
2. 统一 Markdown 报告模板。
3. 建立 claim-level evidence 数据结构。
4. 建立 canonical reference 和 metadata QC 总表。
5. 区分 current-study finding 与 external evidence。
6. 标记报告状态：Ready / Caution / Partial / Superseded。
7. 提供 copy-ready manuscript text。
8. 输出机器可读文件，便于后续自动汇总、去重和质量控制。
9. 改善用户体验，使科研工作者能快速知道“该用哪份、怎么用、有什么风险”。

---

## 2. 总体开发路线图

| 阶段 | 名称 | 核心目标 | 主要产物 |
|---:|---|---|---|
| Phase 0 | 需求冻结与现状盘点 | 明确当前输出问题和目标格式 | 需求说明、现有报告清单 |
| Phase 1 | 项目总索引 | 为所有 evidence package 建立 dashboard | `PROJECT_SUMMARY.md` |
| Phase 2 | 统一报告模板 | 统一所有 Markdown 输出结构 | `REPORT_TEMPLATE.md` |
| Phase 3 | 报告状态与版本关系 | 标记 Ready/Caution/Partial/Superseded | 报告状态字段、版本映射 |
| Phase 4 | Claim 证据矩阵工程化 | 结构化保存 claim、证据等级和风险 | `evidence_claims_master.tsv` |
| Phase 5 | 引用与 Metadata QC 总表 | 解决重复文献、错误 key、RIS 混乱 | `reference_qc_master.tsv` |
| Phase 6 | Copy-ready 写作输出 | 区分审查文本和可直接复制文本 | `quick_use.md` 或 copy-ready section |
| Phase 7 | 搜索可复现性 | 标准化 Zotero/PubMed 查询日志 | `search_log.json` |
| Phase 8 | 自动化生成脚本 | 自动扫描文件夹并生成总览与表格 | Python/Node 脚本 |
| Phase 9 | 用户体验优化 | 降低阅读和选择成本 | 命名规范、导航链接、README |
| Phase 10 | 验证与回归测试 | 确保输出稳定、路径正确、引用一致 | 测试清单、样例输出 |

---

## 3. 推荐目录结构

建议将现有结构逐步改造为：

```text
zotero-evidence-output/
  PROJECT_SUMMARY.md
  README.md
  REPORT_TEMPLATE.md
  reference_qc_master.tsv
  evidence_claims_master.tsv
  final_references_combined.ris

  2026-06-19_004230_epidemiology_sedentary_pcos/
    quick_use.md
    full_evidence_review.md
    references.ris
    reference_qc.tsv
    claims.tsv
    search_log.json

  2026-06-19_005628_mr_bmi_caveat/
    quick_use.md
    full_evidence_review.md
    references.ris
    reference_qc.tsv
    claims.tsv
    search_log.json

  2026-06-19_011400_candidate_gene_mst1r/
    quick_use.md
    full_evidence_review.md
    references.ris
    reference_qc.tsv
    claims.tsv
    search_log.json
```

短期内不必一次性迁移所有旧文件夹，可以先保留旧目录，并在 `PROJECT_SUMMARY.md` 中建立映射。

---

# Phase 0. 需求冻结与现状盘点

## 目标

对现有 `zotero-evidence-output/` 进行盘点，明确：

- 有多少个 evidence package；
- 每个 package 的主题；
- 对应 manuscript section；
- 是否有 RIS 文件；
- 是否存在 PubMed 失败搜索；
- 是否存在 metadata warning；
- 是否应标记为当前可用、需谨慎、未完成或已被取代。

## 开发任务

1. 扫描 `zotero-evidence-output/` 下所有 `.md` 和 `.ris` 文件。
2. 提取每份报告标题、生成时间、主题、Export File、风险提示。
3. 人工或半自动为每份报告添加初始分类。
4. 输出一份临时 inventory。

## 产物

```text
zotero-evidence-output/_inventory_initial.tsv
```

建议字段：

```text
folder
md_file
ris_file
topic
manuscript_section
generated_at
status
main_risk
notes
```

## AI 提示词

```text
你是一名科研证据管理系统工程师。请扫描当前 zotero-evidence-output 文件夹中的所有 Markdown 和 RIS 文件，并生成一个 evidence package inventory。

对每个子文件夹，请提取：
1. 文件夹名称；
2. Markdown 报告文件名；
3. RIS 文件名；
4. 报告标题；
5. 主题；
6. 适用论文部分；
7. 生成日期；
8. 当前状态，使用 Ready / Caution / Partial / Superseded / Unknown；
9. 最高风险；
10. 备注。

如果报告中出现 PubMed query failed、PMOS not verified、no direct evidence、metadata malformed、duplicate Zotero record 等信息，请在 main_risk 或 notes 中标出。

请输出为 Markdown 表格，并同时建议 TSV 字段设计。
```

---

# Phase 1. 项目总索引 PROJECT_SUMMARY.md

## 目标

在 `zotero-evidence-output/` 根目录创建一个总览文件，让用户不用逐个打开子文件夹，也能快速知道每个报告的用途和风险。

## 开发任务

1. 创建 `PROJECT_SUMMARY.md`。
2. 为每个 evidence package 建立一行摘要。
3. 添加“推荐使用顺序”。
4. 添加“高风险 claim 总览”。
5. 添加“最终推荐引用包”说明。

## 产物

```text
zotero-evidence-output/PROJECT_SUMMARY.md
```

建议结构：

```markdown
# Zotero Evidence Output Project Summary

## 1. Executive Dashboard

| Topic | Folder | Status | Main conclusion | Use in manuscript | Main risk | RIS |
|---|---|---|---|---|---|---|

## 2. Recommended Use Order

## 3. High-risk Claims

## 4. Reports Marked Partial or Superseded

## 5. Reference and Metadata Notes

## 6. Next Actions
```

## AI 提示词

```text
你是一名科研项目文档架构师。请根据 zotero-evidence-output 下的多个 evidence review Markdown 报告，生成一个根目录 PROJECT_SUMMARY.md。

要求：
1. 用中文撰写，但保留必要英文术语，例如 claim、evidence、RIS、PubMed、Zotero。
2. 建立 Executive Dashboard 表格，字段包括：Topic、Folder、Status、Main conclusion、Use in manuscript、Main risk、RIS file。
3. Status 只能使用 Ready、Caution、Partial、Superseded、Unknown。
4. 将以下类型标记为高风险：
   - no direct evidence found；
   - PubMed query failed；
   - citation not verified；
   - metadata malformed；
   - duplicate Zotero record；
   - claim contradicted by retrieved evidence。
5. 增加 Recommended Use Order，告诉科研用户写论文时应该优先使用哪些报告。
6. 增加 High-risk Claims 列表，列出不建议直接写入论文的表述及替代表达。
7. 所有路径必须使用相对路径，不要使用绝对路径。
8. 输出完整 Markdown。
```

---

# Phase 2. 统一 Markdown 报告模板

## 目标

统一所有 evidence review 的结构，减少后续解析和人工阅读成本。

## 开发任务

1. 新建 `REPORT_TEMPLATE.md`。
2. 规定所有新报告必须包含固定 section。
3. 将可直接复制文本、证据审查文本、风险提示分开。
4. 标准化 metadata 和 export file 字段。

## 产物

```text
zotero-evidence-output/REPORT_TEMPLATE.md
```

推荐模板：

```markdown
# Evidence Review: {topic}

## Metadata
- Project:
- Manuscript section:
- Input claim:
- Generated:
- Status:
- Evidence package:
- RIS file:

## Executive Summary

## Copy-ready Manuscript Text

## Annotated Recommended Text

## Claims to Revise or Remove

## Claim–Evidence Matrix

## Citation Placement

## Evidence Logic Chain

## Reference Table

## Search Reproducibility

## Zotero Search Summary

## PubMed Expansion

## Reviewer-risk Assessment

## Metadata Quality Control

## Export Files
```

## AI 提示词

```text
你是一名科研写作工具产品经理和 Markdown 模板设计师。请为 Zotero evidence review 工作流设计一个统一的 Markdown 报告模板。

模板必须满足以下要求：
1. 支持科研工作者快速复制可用段落；
2. 支持 reviewer-risk 预判；
3. 支持 claim-level evidence audit；
4. 支持 Zotero/PubMed 搜索可复现性记录；
5. 支持 metadata QC 和 RIS 导出说明；
6. 支持机器解析，因此 section 标题必须固定；
7. 必须区分 Copy-ready Manuscript Text 和 Annotated Recommended Text；
8. 必须包含 Claims to Revise or Remove；
9. 必须包含 Evidence Logic Chain；
10. 输出为完整 Markdown 模板，并在每个 section 下写明填写说明。
```

---

# Phase 3. 报告状态与版本关系

## 目标

解决多个主题相近报告之间的“版本漂移”和“用户不知道该用哪个”的问题。

## 状态定义

| Status | 含义 |
|---|---|
| Ready | 可直接作为当前证据包使用 |
| Caution | 可用，但存在重要 caveat，必须谨慎表述 |
| Partial | 搜索或验证未完成，不应作为最终证据包 |
| Superseded | 已被后续报告替代，仅保留历史记录 |
| Unknown | 尚未评估 |

## 开发任务

1. 为每个报告添加 Status。
2. 在 `PROJECT_SUMMARY.md` 中标记 superseded 关系。
3. 如果同一主题有多个报告，指定 canonical report。
4. 在旧报告顶部添加提示。

## 产物

更新：

```text
PROJECT_SUMMARY.md
每个 full_evidence_review.md 的 Metadata section
```

## AI 提示词

```text
你是一名科研证据审查负责人。请根据多个 evidence review 报告之间的主题重叠和内容完整性，为每个报告指定状态。

状态只能使用：Ready、Caution、Partial、Superseded、Unknown。

判断规则：
1. 如果报告中有 PubMed query failed、citation not verified、PMOS unresolved、TSKU search failed 等问题，优先标记为 Partial 或 Caution。
2. 如果报告的主题已被更新、更完整的后续报告覆盖，标记为 Superseded。
3. 如果报告结构完整、RIS 生成完整、无重大未解决问题，标记为 Ready。
4. 如果报告结论可用但存在高风险 claim，例如 no direct evidence for direct pleiotropy、BMI-independent claim 不稳，则标记为 Caution。

请输出：
1. 每个报告的状态表；
2. canonical report 建议；
3. superseded mapping；
4. 每个 Partial/Caution 报告需要补做的工作。
```

---

# Phase 4. Claim 证据矩阵工程化

## 目标

将每个 Markdown 中的 Claim–Evidence Matrix 提取为结构化数据，形成项目级 claim registry。

## 开发任务

1. 设计 claim-level TSV 字段。
2. 从现有报告中提取 claim。
3. 为每个 claim 标记 evidence level。
4. 统一 evidence level 定义。
5. 生成 `evidence_claims_master.tsv`。

## 推荐 evidence level

| Level | 含义 |
|---|---|
| A | Direct evidence for exact claim |
| B | Direct evidence for closely related claim |
| C | Biological or methodological plausibility only |
| D | Current-study finding; external evidence contextual only |
| E | Unsupported, contradicted, or requires verification |

## 推荐字段

```text
claim_id
package
manuscript_section
original_claim
recommended_wording
evidence_level
evidence_type
directness
recommended_citations
reviewer_risk
action
notes
```

## AI 提示词

```text
你是一名 claim-level evidence audit 专家。请从给定 evidence review Markdown 中提取所有 Claim–Evidence Matrix 信息，并转换为结构化 TSV 表。

字段必须包括：
claim_id、package、manuscript_section、original_claim、recommended_wording、evidence_level、evidence_type、directness、recommended_citations、reviewer_risk、action、notes。

Evidence level 使用：
A = direct evidence for exact claim；
B = direct evidence for closely related claim；
C = biological or methodological plausibility only；
D = current-study finding; external evidence contextual only；
E = unsupported, contradicted, or requires verification。

Action 使用：keep、hedge、revise、remove、verify、cite_current_study_only。

请特别标记以下风险：
1. direct shared genetic architecture not externally established；
2. BMI-independent LST-PCOS association not externally supported；
3. MST1R ovarian function direct evidence absent；
4. PMOS concept not verified；
5. cerebellar enrichment external support absent；
6. PubMed search failed；
7. duplicate or malformed Zotero metadata。

请输出 Markdown 表格和 TSV 内容两种格式。
```

---

# Phase 5. 引用与 Metadata QC 总表

## 目标

建立项目级 canonical reference registry，解决重复 Zotero key、错误 PMID、作者字段异常、RIS 不一致等问题。

## 开发任务

1. 汇总所有报告中的 Reference Table 和 Metadata QC。
2. 按 DOI、PMID、title 进行去重。
3. 指定 canonical Zotero key。
4. 标记 duplicate keys 和 replaced keys。
5. 标记 metadata source of truth：PubMed / Zotero / DOI / manual。
6. 生成 `reference_qc_master.tsv`。
7. 为最终 manuscript 生成合并 RIS。

## 产物

```text
zotero-evidence-output/reference_qc_master.tsv
zotero-evidence-output/final_references_combined.ris
```

## 推荐字段

```text
short_citation
year
title
canonical_zotero_key
duplicate_keys
doi
pmid
pmcid
source_used_for_metadata
used_in_packages
include_in_final_ris
metadata_warnings
```

## AI 提示词

```text
你是一名 Zotero 引用质量控制工程师。请根据多个 evidence review 报告中的 Reference Table 和 Metadata Quality Control 信息，生成项目级 reference_qc_master.tsv。

要求：
1. 按 DOI、PMID、title 去重；
2. 为每篇文献指定 canonical_zotero_key；
3. 将 duplicate_keys、replaced_keys、malformed metadata、missing PMID、invalid PMID、author field malformed 等问题写入 metadata_warnings；
4. 标记 source_used_for_metadata，取值为 PubMed、Zotero、DOI、manual、unknown；
5. 标记 include_in_final_ris，取值为 yes、no、optional、verify；
6. 标记 used_in_packages，列出使用该文献的 evidence package；
7. 对 PubMed-only 但重要的记录，标记为 import_to_zotero_recommended；
8. 输出 Markdown 表格和 TSV 内容。

请特别检查：
- Dapas and Dunaif 2022 作者字段异常；
- Zhao 2025 duplicate record；
- Shao 2026 Zotero key 不一致；
- Moran 2013 duplicate record；
- TSKU 相关记录 PubMed 搜索失败；
- Wang 2022 Nature Genetics PMID 缺失或作者列表过长；
- Wang 2022 JCI Insight invalid PMID = 0。
```

---

# Phase 6. Copy-ready 写作输出

## 目标

让科研用户快速获得可以直接放入 manuscript 的文本，同时保留 annotated 审查版本。

## 开发任务

1. 在每个报告中添加 `Copy-ready Manuscript Text`。
2. 删除内部备注，例如“需要验证 citation 2”。
3. 保留谨慎措辞。
4. 另设 `Annotated Recommended Text` 解释每句证据来源。
5. 为高风险 claim 提供替代表述。

## 产物

每个 evidence package 中：

```text
quick_use.md
```

建议结构：

```markdown
# Quick Use: {topic}

## Use Status

## Copy-ready Manuscript Text

## Must-cite References

## Claims to Avoid

## Safer Replacements

## Reviewer-risk Notes

## RIS File
```

## AI 提示词

```text
你是一名医学遗传学论文写作编辑。请把给定 evidence review 报告转换为 quick_use.md。

要求：
1. 输出中文说明，但 manuscript text 用英文；
2. manuscript text 必须可以直接复制到论文中；
3. 删除所有内部备注，例如“citation should be verified directly”；
4. 如果存在未验证概念，例如 PMOS，请不要在 copy-ready text 中强行写入，除非以 very cautious wording 表达；
5. 增加 Must-cite References；
6. 增加 Claims to Avoid；
7. 增加 Safer Replacements；
8. 增加 Reviewer-risk Notes；
9. 所有 claim 必须区分 current-study finding 与 external evidence；
10. 不要创造新引用，不要夸大外部证据。
```

---

# Phase 7. 搜索可复现性与 Search Log

## 目标

使 Zotero/PubMed 检索过程可复现、可审计、可补做。

## 开发任务

1. 为每个 evidence package 生成 `search_log.json`。
2. 标准化记录 Zotero search、PubMed query、失败搜索、筛选规则。
3. 标记是否 full-text inspected。
4. 标记 PubMed-only records 是否导入 Zotero。

## 推荐 JSON 字段

```json
{
  "package": "",
  "date": "",
  "zotero_searches": [
    {
      "mode": "semantic|keyword|tag",
      "query": "",
      "hits": 0,
      "included": 0,
      "notes": ""
    }
  ],
  "pubmed_searches": [
    {
      "query": "",
      "max_results": 20,
      "sort": "relevance|date",
      "status": "completed|failed|partial",
      "error": "",
      "included_pmids": []
    }
  ],
  "inclusion_criteria": [],
  "exclusion_criteria": [],
  "full_text_inspected": "yes|no|partial",
  "unresolved_gaps": []
}
```

## AI 提示词

```text
你是一名科研检索可复现性审计员。请根据 evidence review Markdown 中的 Zotero Search Summary 和 PubMed Expansion，生成 search_log.json。

要求：
1. 提取所有 Zotero semantic search、keyword search、tag search；
2. 提取所有 PubMed query；
3. 标记每个 PubMed search 的状态：completed、failed、partial；
4. 如果出现 Too Many Requests、query failed、limited yield、fetch issue，请写入 error 字段；
5. 记录 included PMIDs；
6. 记录 excluded PubMed-only records 及原因；
7. 标记 full_text_inspected 为 yes、no 或 partial；
8. 写出 unresolved_gaps；
9. 输出合法 JSON，不要输出 Markdown。
```

---

# Phase 8. 自动化生成脚本

## 目标

用脚本自动扫描 evidence output，并生成总览、claims 表、reference QC 表和基本状态提示。

## 开发任务

1. 选择实现语言：建议 Python。
2. 扫描目录结构。
3. 解析 Markdown section。
4. 提取 Reference Table、Metadata QC、Export File。
5. 生成 project summary 初稿。
6. 生成 claims 和 references TSV 初稿。
7. 检查路径是否为绝对路径。
8. 检查 RIS 文件是否存在。

## 推荐脚本

```text
scripts/evidence_output_audit.py
```

推荐功能：

```bash
python scripts/evidence_output_audit.py \
  --input zotero-evidence-output \
  --write-summary \
  --write-claims \
  --write-reference-qc
```

## AI 提示词

```text
你是一名 Python 工程师。请为 Zotero evidence output 文件夹编写一个审计脚本 scripts/evidence_output_audit.py。

功能要求：
1. 输入参数 --input，默认为 zotero-evidence-output；
2. 扫描所有子文件夹中的 Markdown 和 RIS 文件；
3. 识别每个 evidence package 的主 Markdown；
4. 提取标题、Generated、Source、PubMed status、Export File、Metadata Quality Control、Gaps and Reviewer-risk Assessment；
5. 检测绝对路径，尤其是 /Users/ 开头路径，并报告；
6. 检测 Markdown 中声明的 RIS 文件是否真实存在；
7. 根据关键词初步判断 Status：Ready、Caution、Partial、Unknown；
8. 生成 PROJECT_SUMMARY.draft.md；
9. 生成 evidence_claims_master.draft.tsv；
10. 生成 reference_qc_master.draft.tsv；
11. 不要修改原始报告，除非显式传入 --write；
12. 代码应简洁、可维护，不依赖大型外部库。

请输出完整 Python 文件。
```

---

# Phase 9. 用户体验优化

## 目标

降低用户查找、阅读、比较和复制内容的成本。

## 开发任务

1. 统一文件夹命名规则。
2. 为旧文件夹建立主题别名。
3. 在根目录 README 中解释状态含义。
4. 每个 report 顶部加入 Use Status。
5. 每个 report 加入返回 `PROJECT_SUMMARY.md` 的链接。
6. 避免绝对路径。
7. 每个 package 提供 quick_use。

## 推荐命名规则

```text
YYYY-MM-DD_HHMMSS_{topic_slug}/
```

示例：

```text
2026-06-19_004230_epidemiology_sedentary_pcos/
2026-06-19_005628_mr_bmi_caveat/
2026-06-19_011400_candidate_gene_mst1r/
2026-06-19_012712_candidate_genes_tank_tsku/
2026-06-19_0155_single_cell_ovary/
2026-06-19_020100_limitations_paragraph/
2026-06-19_021111_gwas_architecture/
```

## AI 提示词

```text
你是一名科研软件用户体验设计师。请为 zotero-evidence-output 设计用户友好的文件夹命名、README 和导航规范。

要求：
1. 保留时间戳，但必须加入可读 topic_slug；
2. 定义 Ready、Caution、Partial、Superseded、Unknown 的用户解释；
3. 每个 evidence package 应包含 quick_use.md、full_evidence_review.md、references.ris、reference_qc.tsv、claims.tsv、search_log.json；
4. 所有 Markdown 顶部都应有返回 PROJECT_SUMMARY.md 的链接；
5. 所有路径使用相对路径；
6. 设计一个 README.md 草稿，告诉科研用户如何选择报告、如何使用 RIS、如何处理高风险 claim；
7. 输出完整 Markdown。
```

---

# Phase 10. 验证与回归测试

## 目标

确保工程化改造不会破坏现有内容，并保证输出可用、路径正确、引用一致。

## 测试清单

| 测试项 | 标准 |
|---|---|
| Markdown 文件存在 | 每个 package 至少有一个主报告 |
| RIS 文件存在 | Export File 指向的 RIS 应存在 |
| 无绝对路径 | 不应出现 `/Users/...` 等本地绝对路径 |
| 状态字段存在 | 每个新报告必须有 Status |
| Copy-ready text 存在 | 每个 Ready/Caution 报告应有 |
| Claim matrix 可解析 | 有固定表头或 TSV |
| Reference QC 可解析 | 有 DOI/PMID/key 字段 |
| PubMed failed 被标记 | 不能隐藏失败搜索 |
| Superseded 有映射 | 旧报告应指向 canonical report |
| 高风险 claim 有替代表述 | 不仅指出问题，还给 safer wording |

## AI 提示词

```text
你是一名科研证据工作流 QA 工程师。请对 zotero-evidence-output 的工程化输出进行质量检查。

检查内容：
1. PROJECT_SUMMARY.md 是否存在；
2. 每个子文件夹是否至少包含主 Markdown；
3. 每个声明的 RIS 文件是否存在；
4. 是否存在 /Users/ 开头的绝对路径；
5. 每个报告是否有 Status；
6. Ready 或 Caution 报告是否有 Copy-ready Manuscript Text；
7. 是否存在 PubMed query failed 但 Status 未标记为 Partial 或 Caution；
8. 是否存在 no direct evidence found 但 recommended text 仍然过度肯定；
9. 是否存在 duplicate Zotero key 未写入 reference QC；
10. 是否存在 current-study finding 被外部文献错误背书。

请输出 QA 报告，包括：
- Passed checks；
- Failed checks；
- Warnings；
- Required fixes；
- Suggested fixes。
```

---

## 4. 开发优先级建议

### P0：必须优先完成

1. `PROJECT_SUMMARY.md`
2. `REPORT_TEMPLATE.md`
3. 报告 Status 标记
4. 高风险 claim 总表
5. 绝对路径修正

### P1：强烈建议完成

1. `reference_qc_master.tsv`
2. `evidence_claims_master.tsv`
3. `quick_use.md`
4. `search_log.json`
5. canonical report / superseded mapping

### P2：后续增强

1. 自动化审计脚本
2. RIS 合并与去重
3. Zotero duplicate 检测
4. HTML dashboard
5. 与论文写作 workflow 集成

---

## 5. 关键工程原则

### 1. 科研安全优先

所有输出必须避免把 biological plausibility 写成 direct evidence。

推荐规则：

```text
如果证据不是 exact claim direct support，则必须 hedge。
```

### 2. Current-study finding 与 external evidence 必须分开

例如：

```text
Current study: LST-PCOS polygenic overlap observed.
External evidence: PCOS shares architecture with obesity and LST is genetically tractable.
Conclusion: plausible convergence, not proven horizontal pleiotropy.
```

### 3. 所有失败搜索都必须显式记录

不能把 PubMed failed query 隐藏在长文末尾。

### 4. 所有路径必须相对化

不应在报告中出现：

```text
/Users/daxuan/Desktop/...
```

应改为：

```text
zotero-evidence-output/{package}/{file}.ris
```

### 5. 每个高风险 claim 必须有 safer replacement

例如：

| 高风险表述 | 替代表述 |
|---|---|
| sedentary behavior and PCOS share causal variants | may have partly convergent genetic and biological architectures |
| BMI-independent LST-PCOS association is established | BMI may partly mediate or confound the LST-PCOS association |
| MST1R is implicated in ovarian function | MST1R/RON biology is consistent with inflammatory and metabolic contexts relevant to PCOS |
| cerebellar enrichment is externally validated | cerebellar enrichment is a present-study signal requiring validation |

---

## 6. 样例 PROJECT_SUMMARY 表格草案

| Topic | Folder | Status | Main conclusion | Use in manuscript | Main risk |
|---|---|---|---|---|---|
| Epidemiology of sedentary behavior and PCOS | `sedentary_behavior_pcos_2026-06-19_004230/` | Caution | Epidemiological evidence is heterogeneous; population-based studies support lower PA/higher sitting in PCOS | Introduction / Discussion | Direct sedentary-PCOS shared genetic architecture is not externally replicated |
| LST-PCOS MR and BMI caveat | `sedentary_behavior_pcos_2026-06-19_005628/` | Caution | LST-PCOS MR evidence exists, but BMI-independent claim should be weakened | Discussion | BMI independence not supported as written |
| MST1R candidate gene | `mst1r_sedentary_pcos_2026-06-19_011400/` | Caution | MST1R/RON biology supports inflammatory/metabolic plausibility | Candidate gene discussion | No direct MST1R-PCOS ovarian evidence found |
| TANK/TSKU candidate genes | `tank_tsku_pcos_2026-06-19_012712/` | Partial | TANK and TSKU are biologically plausible candidates | Candidate gene discussion | TSKU PubMed query failed |
| Multisystem mechanisms | `lst_pcos_multisystem_2026-06-19_014935/` | Caution | Multisystem interpretation is plausible | Discussion | Cerebellar/PI3K-Akt/AMPK/immune claims need hedging |
| PCOS multisystem framing | `sedentary_behavior_pcos_2026-06-19_015320/` | Partial | PCOS multisystem framing supported | Discussion | PMOS concept not verified |
| Single-cell ovarian context | `sedentary_behavior_pcos_2026-06-19_0155/` | Caution | Granulosa/macrophage enrichment is plausible but not definitive | Results / Discussion | BMI-independent genetic claim is current-study only |
| Limitations paragraph | `sedentary_behavior_pcos_2026-06-19_020100/` | Ready | Limitation wording is well supported with cautious phrasing | Limitations | Propensity score matching lacks dedicated methods citation |
| GWAS architecture final review | `sedentary_behavior_pcos_gwas_2026-06-19_021111/` | Caution | Direct horizontal pleiotropy is not established; frame as knowledge gap | Discussion | Avoid overclaiming shared causal variants |

---

## 7. 最终交付定义

本工程化改造完成后，用户应能做到：

1. 打开 `PROJECT_SUMMARY.md`，一分钟内知道每个报告的用途。
2. 对每个 manuscript claim，知道证据等级、风险和替代表述。
3. 对每篇文献，知道 canonical Zotero key、DOI、PMID 和是否可进入最终 RIS。
4. 对每个报告，知道是否 Ready、Caution、Partial 或 Superseded。
5. 直接复制 `quick_use.md` 中的 manuscript text。
6. 复现 Zotero/PubMed 检索过程。
7. 自动检测绝对路径、丢失 RIS、重复引用和高风险 claim。

---

## 8. 下一步建议

建议按以下顺序执行：

1. 先生成 `PROJECT_SUMMARY.md`。
2. 再生成 `REPORT_TEMPLATE.md`。
3. 对现有 9 个 Markdown 报告进行状态标记。
4. 手动建立第一版 `reference_qc_master.tsv`。
5. 手动建立第一版 `evidence_claims_master.tsv`。
6. 为 2-3 个最重要报告试点生成 `quick_use.md`。
7. 最后再写自动化脚本批量处理。

优先试点报告建议：

1. `sedentary_behavior_pcos_gwas_2026-06-19_021111`：用于 GWAS architecture 总结。
2. `sedentary_behavior_pcos_2026-06-19_020100`：用于 limitations paragraph。
3. `mst1r_sedentary_pcos_2026-06-19_011400`：用于 candidate gene 风险控制。

---

## 9. 总结

本计划的核心不是单纯“美化 Markdown”，而是把 evidence review 从一次性文本输出升级为一个具备以下能力的工程化系统：

- 可追踪；
- 可复现；
- 可去重；
- 可比较；
- 可直接用于论文写作；
- 可经受 reviewer 和共同作者审查。

完成后，`zotero-evidence-output/` 将不再只是报告堆积目录，而是一个面向科研写作的 evidence intelligence workspace。
