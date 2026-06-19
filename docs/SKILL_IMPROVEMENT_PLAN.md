# zotero-evidence-review Skill 工程化改进计划

生成日期：2026-06-19  
对象：`zotero-evidence-review/SKILL.md` 及其相关 skill 工作流  
目标：提升 skill 的输出质量、证据推理质量、科研可用性、用户体验和可维护性。  
说明：本计划**不是**改进某一次 `zotero-evidence-output/` 输出文件夹，而是用这些输出中暴露的问题反向改进 `zotero-evidence-review` skill 本身。

---

## 1. 背景与诊断

当前 `zotero-evidence-review` skill 已经具备较完整的 Zotero + PubMed 证据审查工作流，包括：

- 意图识别；
- Zotero 语义检索与结构化检索；
- 段落主张抽取；
- Claim–Evidence Matrix；
- PubMed 扩展检索；
- Markdown evidence report；
- EndNote RIS 导出；
- Metadata QC；
- Citation verification。

但从实际输出可以反向看到，skill 仍有改进空间：

1. 报告内容丰富，但缺少统一的 package status，例如 Ready / Caution / Partial / Superseded。
2. 对 current-study finding 与 external evidence 的区分还不够强制。
3. Evidence strength 标签不够标准化，不同报告之间存在表达漂移。
4. PubMed failed、citation not verified、no direct evidence found 等高风险信息有时不够前置。
5. Recommended Manuscript Text 有时混入审查备注，不完全 copy-ready。
6. 同一主题多次运行时，skill 没有内置 canonical report / superseded 机制。
7. RIS 与 reference QC 虽有规则，但缺少更强的 canonical-reference gate。
8. 搜索可复现性已有记录，但没有统一 schema。
9. 默认只输出 Markdown + RIS，有利于简洁，但限制了后续结构化质量追踪。
10. 最终 chat summary 只列路径和 warnings，缺少“这份报告如何使用”的风险等级。

核心改进目标：把 skill 从“能生成证据报告”升级为“能生成科研安全、结构稳定、风险可见、可复用的 evidence intelligence package”。

---

## 2. 总体改进路线图

| 阶段 | 名称 | 改进对象 | 核心目标 |
|---:|---|---|---|
| Phase 0 | Skill 现状审计 | `SKILL.md` | 明确已有规则与缺口 |
| Phase 1 | Evidence Package 状态模型 | Module 2.5 | 增加 Ready/Caution/Partial/Superseded |
| Phase 2 | Evidence Level 标准化 | Module 2、2.5、Appendix | 统一 A-E 证据等级 |
| Phase 3 | Current-study vs External Evidence 分离 | Module 2、2.5 | 防止外部文献错误背书 |
| Phase 4 | Copy-ready 与 Annotated 双层输出 | Report template | 提升论文写作可用性 |
| Phase 5 | Critical Warnings 前置 | Report template + final chat | 让高风险信息醒目 |
| Phase 6 | Search Reproducibility Schema | Zotero/PubMed summary | 标准化检索日志 |
| Phase 7 | Reference Canonicalization Gate | Metadata QC + RIS | 强化引用去重和 canonical key |
| Phase 8 | Run Relationship 与 Superseded 机制 | Output workflow | 处理多次运行同主题报告 |
| Phase 9 | Skill 自检提示词与 QA | Quality Gates | 防止过度推断和格式漂移 |
| Phase 10 | Skill 文档重构与验证 | `SKILL.md` | 将规则落入 skill spec |

---

# Phase 0. Skill 现状审计

## 目标

审计 `zotero-evidence-review/SKILL.md`，判断当前模块是否已经支持高质量科研证据输出，以及哪些规则需要增强。

## 检查点

1. Intent Detection 是否覆盖中文科研用户的常见输入。
2. Module 2 是否足够区分 direct evidence、indirect evidence、mechanistic evidence、current-study finding。
3. Module 2.5 是否有 package status 判断。
4. Markdown Report Requirements 是否有 copy-ready text。
5. Metadata QC 是否强制 canonical reference。
6. PubMed failed / not executed / completed 是否在报告前部可见。
7. Quality Gates 是否检查 causal overclaim、BMI-independent overclaim、horizontal pleiotropy overclaim。
8. Appendix template 是否稳定、可机器解析。

## AI 提示词

```text
你是一名科研 AI workflow 审计工程师。请审计 zotero-evidence-review/SKILL.md，目标是找出会影响 evidence review 输出质量的问题。

请重点检查：
1. 是否强制区分 current-study findings 与 external literature evidence；
2. 是否存在统一的 evidence level 体系；
3. 是否在报告开头展示 status 和 critical warnings；
4. 是否区分 copy-ready manuscript text 与 annotated recommendation；
5. 是否有 PubMed failed / citation unverified / no direct evidence 的前置风险提醒；
6. 是否有 search reproducibility schema；
7. RIS 生成前是否有 canonical reference gate；
8. 是否有 QA self-audit，防止 causal overclaim、BMI-independent overclaim、direct pleiotropy overclaim。

输出：
- 已有优点；
- 缺失规则；
- 高优先级改进；
- 建议插入到 SKILL.md 的位置；
- 可以直接复制进 SKILL.md 的规则草案。
```

---

# Phase 1. Evidence Package 状态模型

## 目标

让 skill 在每次生成 evidence report 时，自动给报告赋予使用状态，帮助用户判断是否可直接用于论文。

## 状态定义

| Status | 含义 | 用户使用建议 |
|---|---|---|
| Ready | 检索完成、证据直接、metadata 无重大问题 | 可直接用于写作 |
| Caution | 可用但有重要 caveat | 必须使用 hedge wording |
| Partial | 检索失败、关键 citation 未验证、metadata 未完成 | 不建议作为最终证据包 |
| Superseded | 已被后续报告替代 | 仅保留历史记录 |
| Unknown | 无法判断 | 需要人工检查 |

## 触发规则

- PubMed query failed → 至少 `Partial` 或 `Caution`。
- PMOS / concept / citation not verified → `Partial` 或 `Caution`。
- no direct evidence for central claim → `Caution`。
- metadata mismatch unresolved → `Partial`。
- duplicate unresolved but excluded safely → `Caution`。
- all required evidence inspected and risks low → `Ready`。

## 建议插入到 SKILL.md 的位置

- Module 2.5 `Markdown Report Requirements` 前后；
- Appendix `EVIDENCE_REVIEW_REPORT` 的 metadata 区；
- Final chat output warning 格式。

## AI 提示词

```text
你是 zotero-evidence-review skill 的工作流设计师。请为 Evidence Package Export 模块设计一个自动状态判断系统。

要求：
1. 状态只能使用 Ready、Caution、Partial、Superseded、Unknown；
2. 给出每个状态的定义、触发条件和用户使用建议；
3. 给出哪些风险必须使状态降级，例如 PubMed failed、no direct evidence、metadata mismatch、citation not verified；
4. 给出应插入到 Markdown report Metadata section 的字段；
5. 给出最终 chat summary 应如何显示状态；
6. 输出可直接复制进 SKILL.md 的 Markdown 规则。
```

---

# Phase 2. Evidence Level 标准化

## 目标

让所有 claim 使用统一的 evidence level，减少不同报告中的证据强度标签漂移。

## 建议等级

| Level | 名称 | 定义 | 推荐措辞 |
|---|---|---|---|
| A | Exact direct support | 外部文献直接支持 exact claim | supported / directly supported |
| B | Close direct support | 直接支持相近 claim，但不是完全相同 | consistent with / supports related claim |
| C | Plausibility support | 机制、背景、review 或 pathway plausibility | biologically plausible / may align with |
| D | Current-study only | 主要是用户当前研究结果，外部文献仅背景 | in our analysis / our findings suggest |
| E | Unsupported / contradicted / verify | 未支持、相矛盾或需要验证 | remove / verify / hedge strongly |

## 需要修改的输出位置

- Claim–Evidence Matrix 增加 `Evidence level`。
- Reviewer-risk Assessment 使用相同等级。
- Recommended Manuscript Text 根据等级自动 hedge。

## AI 提示词

```text
你是一名科研证据分级方法学专家。请为 zotero-evidence-review skill 设计统一 evidence level 体系。

要求：
1. 使用 A、B、C、D、E 五级；
2. 每级必须包含定义、判断标准、推荐措辞和不推荐措辞；
3. 明确 D = current-study only，不能用外部文献当作直接证明；
4. 明确 E = unsupported、contradicted 或 requires verification；
5. 给出 Claim–Evidence Matrix 的新表头；
6. 给出可复制进 SKILL.md 的规则文本。
```

---

# Phase 3. Current-study Finding 与 External Evidence 分离

## 目标

防止 skill 把用户当前研究中的统计结果、enrichment、SMR/TWAS、candidate gene prioritization 等结果，用外部文献错误地“证明”。

## 新规则

在所有报告中，claim 必须标记来源层级：

| Source layer | 含义 |
|---|---|
| Current study | 用户提供或当前分析得到的结果 |
| Zotero external evidence | Zotero 文献证据 |
| PubMed external evidence | PubMed 扩展文献证据 |
| Interpretive bridge | 基于当前结果与外部证据之间的推断 |
| Unsupported gap | 未找到证据 |

## 必须使用的表达

- Current study: `In our analysis...`, `The present study identified...`
- External evidence: `Previous studies show...`, `Published evidence supports...`
- Interpretive bridge: `These findings are consistent with...`, `may suggest...`
- Unsupported gap: `requires validation`, `was not directly supported by retrieved evidence`

## AI 提示词

```text
你是一名科研写作证据边界审查员。请为 zotero-evidence-review skill 设计规则，强制区分 current-study findings 与 external evidence。

要求：
1. 定义 Current study、Zotero external evidence、PubMed external evidence、Interpretive bridge、Unsupported gap；
2. 说明哪些类型的 claim 必须标记为 Current study，例如 SMR、TWAS、MAGMA、colocalization、cell enrichment、candidate gene prioritization；
3. 说明外部文献只能支持 biological plausibility，不能证明用户当前分析结果；
4. 给出推荐句式和禁止句式；
5. 给出 Claim–Evidence Matrix 的新增列；
6. 输出可直接复制到 SKILL.md 的 Markdown 规则。
```

---

# Phase 4. Copy-ready 与 Annotated 双层输出

## 目标

让报告同时服务两类需求：

1. 科研用户直接复制到 manuscript；
2. 用户查看证据审查理由和风险。

## 新增 section

在 `EVIDENCE_REVIEW_REPORT` 中新增：

```markdown
## 2. 可直接使用的稿件文本（Copy-ready Manuscript Text）

## 3. 注释版推荐文本（Annotated Recommended Text）
```

Copy-ready text 要求：

- 不包含内部备注；
- 不写“citation should be verified”；
- 不写 workflow 解释；
- 保留谨慎措辞；
- 使用 manuscript 原语言。

Annotated text 要求：

- 可解释每个 citation placement；
- 可指出 caveat；
- 可说明哪些句子来自 current study，哪些来自 external evidence。

## AI 提示词

```text
你是一名医学论文编辑和科研证据审查员。请为 zotero-evidence-review skill 设计 copy-ready 与 annotated 双层输出规范。

要求：
1. Copy-ready Manuscript Text 必须可直接复制到论文；
2. 不得包含内部审查备注；
3. Annotated Recommended Text 可以包含证据解释、citation rationale 和风险提示；
4. 如果证据不足，copy-ready text 必须使用 hedge wording；
5. 如果某概念未验证，不得在 copy-ready text 中强行写成事实；
6. 给出 Markdown template；
7. 给出可复制进 SKILL.md 的规则。
```

---

# Phase 5. Critical Warnings 前置

## 目标

让高风险问题在报告开头和最终 chat summary 中立即可见。

## Critical warning 条件

以下情况必须进入报告开头的 `Critical Warnings`：

- PubMed tool unavailable / query failed；
- central claim has no direct evidence；
- external evidence contradicts draft claim；
- citation/concept not verified；
- metadata mismatch unresolved；
- duplicate Zotero records affect selected references；
- current-study finding could be mistaken for external evidence；
- causal wording not supported；
- BMI-independent or horizontal pleiotropy claim not supported directly。

## AI 提示词

```text
你是一名科研审稿风险控制专家。请为 zotero-evidence-review skill 设计 Critical Warnings 前置规则。

要求：
1. 定义哪些情况必须进入 Critical Warnings；
2. Critical Warnings 必须出现在 report metadata 后、核心结论前；
3. 每条 warning 必须包含 affected claim、risk、required action；
4. 最终 chat summary 也必须显示 Status 和 critical warnings；
5. 如果无 critical warnings，写 No critical warnings；
6. 输出可复制进 SKILL.md 的模板和规则。
```

---

# Phase 6. Search Reproducibility Schema

## 目标

让 skill 的 Zotero / PubMed 检索过程可审计、可复现、可补做。

## 新增 report section

```markdown
## Search Reproducibility

| Source | Query | Mode | Max results | Status | Included | Notes |
|---|---|---|---:|---|---:|---|
```

## 必须记录

- Zotero semantic query；
- Zotero keyword query；
- PubMed query；
- PubMed max results；
- PubMed status；
- failed reason；
- included PMIDs；
- excluded records and reason；
- whether full text was inspected。

## AI 提示词

```text
你是一名科研检索可复现性专家。请为 zotero-evidence-review skill 设计 Search Reproducibility section。

要求：
1. 同时覆盖 Zotero semantic search、Zotero keyword search、PubMed search；
2. 必须记录 query、mode、max_results、status、included_count、excluded_reason；
3. PubMed failed 或 unavailable 必须记录 attempted/planned query；
4. 标记 full_text_inspected 为 yes/no/partial；
5. 输出 Markdown 表格模板；
6. 输出可复制进 SKILL.md 的规则。
```

---

# Phase 7. Reference Canonicalization Gate

## 目标

强化 skill 在导出 RIS 前的 canonical reference 判断，减少重复 key、错误 PMID、作者字段异常和重复导出。

## 新增 gate

在 RIS 生成前，每篇 selected reference 必须有：

- canonical identifier: DOI / PMID / Zotero key；
- duplicate check result；
- metadata source of truth；
- RIS action: Include / Exclude / Verify / Optional；
- reason。

## AI 提示词

```text
你是一名 Zotero + PubMed 引用质量控制工程师。请为 zotero-evidence-review skill 设计 Reference Canonicalization Gate。

要求：
1. 每篇 selected reference 必须检查 DOI、PMID、title、first author、year；
2. 如果 DOI 或 PMID 相同，必须合并为同一 canonical record；
3. 如果 Zotero key 多个，必须选择 canonical Zotero key 并记录 duplicate keys；
4. 如果 PubMed 与 Zotero metadata 冲突，必须标记 Possible metadata mismatch；
5. RIS action 只能是 Include、Exclude、Verify、Optional；
6. unresolved mismatch 不得进入 RIS；
7. 输出 QC 表格模板和可复制进 SKILL.md 的规则。
```

---

# Phase 8. Run Relationship 与 Superseded 机制

## 目标

处理同一主题多次运行造成的报告分散和版本漂移。

## 新增规则

当新的 evidence package 与已有 package 主题高度相似时，skill 应：

1. 在报告 metadata 中标记 `Related prior packages`。
2. 不自动修改旧报告，除非用户要求。
3. 在新报告中说明是否可能 supersede 旧报告。
4. 如果用户请求“整理/总结已有输出”，才生成 project-level summary。

## AI 提示词

```text
你是一名科研 evidence workflow 版本管理设计师。请为 zotero-evidence-review skill 设计 run relationship 和 superseded 机制。

要求：
1. 不要求 skill 自动改旧文件；
2. 新报告 metadata 可以列出 related prior packages；
3. 如果新报告更完整，可以写 Potentially supersedes；
4. 如果只是不同 manuscript section，应写 Complementary to；
5. 给出 similarity 判断依据，例如 topic slug、核心关键词、selected references 重叠；
6. 输出可复制进 SKILL.md 的规则。
```

---

# Phase 9. Skill 自检提示词与 QA Gate

## 目标

在 skill 写入文件前后进行自检，避免过度推断、格式漂移、RIS 错误和路径问题。

## QA Gate

写入文件前检查：

- 是否有 status；
- 是否有 critical warnings；
- 是否有 copy-ready text；
- 是否有 claim evidence level；
- 是否区分 current-study 与 external evidence；
- 是否记录 PubMed status；
- RIS 是否只含 RIS 记录；
- 是否存在绝对路径；
- 是否存在 unresolved metadata mismatch；
- 是否把 E-level claim 写得太肯定。

## AI 提示词

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

---

# Phase 10. SKILL.md 落地修改建议

## 建议修改点 1：Module 2.5 增加 Package Status

插入位置：`## 2.5 Evidence Package Export` 的 `Markdown Report Requirements` 前。

建议新增小节：

```markdown
### Evidence Package Status

Every generated evidence package must receive one status: Ready, Caution, Partial, Superseded, or Unknown...
```

## 建议修改点 2：Markdown Report Requirements 更新 section 顺序

当前 section 建议升级为：

```markdown
1. Metadata and Use Status
2. Critical Warnings
3. 核心结论
4. 可直接使用的稿件文本（Copy-ready Manuscript Text）
5. 注释版推荐文本（Annotated Recommended Text）
6. 主张—证据矩阵
7. 引文放置建议
8. Evidence Logic Chain
9. 参考文献表
10. Search Reproducibility
11. Zotero 检索总结
12. PubMed 扩展检索
13. 综合写作建议
14. Claims to Revise or Remove
15. 证据缺口与审稿风险
16. 元数据质量控制
17. 导出文件
```

## 建议修改点 3：Claim–Evidence Matrix 增加列

建议表头：

```markdown
| # | Claim | Source layer | Evidence level | Zotero evidence | PubMed evidence | Evidence status | Confidence | Risk | Recommended action | Recommended citation |
```

## 建议修改点 4：Final chat output 增加 Status

建议格式：

```markdown
Generated Evidence Package:
- Status: Caution
- Markdown report: `...`
- EndNote RIS: `...`

Critical Warnings:
- Direct shared causal variants were not established; use as knowledge gap.
```

---

## 4. 优先级

### P0：必须优先落地

1. Evidence Package Status。
2. Evidence Level A-E。
3. Current-study vs External Evidence 分离。
4. Critical Warnings 前置。
5. Copy-ready Manuscript Text。

### P1：强烈建议落地

1. Search Reproducibility schema。
2. Reference Canonicalization Gate。
3. Claims to Revise or Remove。
4. Final chat summary 显示 Status。
5. QA self-audit gate。

### P2：后续增强

1. Related prior package / superseded 机制。
2. 可选结构化输出 JSON/TSV。
3. skill validator 增加模板字段检查。
4. 项目级 summary 作为用户显式请求时的独立模式。

---

## 5. 最小可行修改方案

如果只做一轮小改，建议优先修改 `SKILL.md` 四处：

1. Module 2.5 增加 `Evidence Package Status`。
2. `Markdown Report Requirements` 增加 `Critical Warnings` 和 `Copy-ready Manuscript Text`。
3. `EVIDENCE_REVIEW_REPORT` 模板增加 `Status`、`Critical Warnings`、`Evidence level`、`Source layer`。
4. `Quality Gates` 增加 overclaim 检查。

这四项就能显著提升输出和思考质量。

---

## 6. 总结

本计划的核心是改进 `zotero-evidence-review` skill 的内在工作流，而不是整理某个输出文件夹。输出文件夹中暴露的问题应转化为 skill 的规则：

- 每份报告必须有状态；
- 每个 claim 必须有证据等级；
- 每个 current-study finding 必须与外部证据分离；
- 每个高风险 claim 必须有 safer wording；
- 每个 RIS 记录必须通过 canonical metadata gate；
- 每次 PubMed 失败必须显式前置；
- 每段推荐文本必须区分 copy-ready 和 annotated。

完成后，skill 的输出将从“完整但偏长的证据报告”升级为“可直接服务科研写作与审稿风险控制的 evidence intelligence workflow”。
