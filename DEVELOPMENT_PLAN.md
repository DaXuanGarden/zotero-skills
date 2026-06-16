# Zotero Evidence Review Skill 改进建议与开发计划

> 目标：将 `zotero-evidence-review` 从“可用的 Zotero 检索技能”升级为“面向科研写作、证据链构建、引用核查和文献管理的稳定工作流技能”。

## 1. 当前状态评估

### 仓库结构

当前仓库已经具备标准 skill 结构：

```text
zotero-skills/
├── README.md
├── Zotero_MCP_OpenCode_Guide.md
└── zotero-evidence-review/
    └── SKILL.md
```

当前 `SKILL.md` 的优点：

1. 已有明确的 frontmatter，包括 `name`、`description`、`license`、`compatibility` 和 `metadata`。
2. 核心场景清晰：语义检索、结构化检索、证据链提取、基于 Zotero 的写作建议。
3. 输出模板较完整，适合论文写作与综述场景。
4. 已经强调优先使用 semantic search，并提供自然语言查询扩展示例。

当前主要可提升点：

1. 还缺少“工具选择决策树”，即什么时候用语义检索、关键词检索、元数据、全文、标注、笔记、collection 等工具。
2. 对 Zotero MCP 的增删改操作缺少安全边界说明。
3. 输出结果中的可追溯字段还可以更标准化，例如 Zotero item key、DOI、PMID、证据类型、可引用位置。
4. 尚未显式规定“不得编造引用”和“没有检索到就明确说明”。
5. 目前更偏 OpenCode 描述，建议补充 ZCode/Zotero MCP 通用使用原则。
6. 证据链模块可以进一步细化为支持证据、反向证据、背景证据、机制证据、方法学证据。
7. 写作建议模块可以进一步区分“补充引用”“弱化因果表述”“术语统一”“证据不足”“需要新增检索”。

### 1.1 开源参考项目调研

作为改进参照，调研了以下开源项目：

| 项目 | 星标 | 亮点 | 对本 skill 的启发 |
|------|------|------|------------------|
| [KellanLow/Zotero-MCP-Usage](https://github.com/KellanLow/Zotero-MCP-Usage) | — | 零容忍全量 PDF 阅读协议、Token 预算管理、反作弊自检 | 引用验证需增加逐页原文核查模式 |
| [yipng05-max/literature-verifier](https://github.com/yipng05-max/-skills) | — | 知网 CDP 直检、中文幻觉模式分类、批量核查、核心期刊验证 | 中文核查需从规则升级为可执行流程 |
| [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | 100+ | PRISMA 系统综述、多数据库集成、引用验证脚本、skill 间组合 | 需增加外部学术 MCP 协同和系统综述工作流 |
| [crossref-academic-mcp-server](https://github.com/AiAgentKarl/crossref-academic-mcp-server) | — | 免费聚合 Crossref+OpenAlex+Semantic Scholar，无需 API Key | Zotero 搜不到时无缝 fallback 到外部源 |
| [Academix](https://github.com/xingyulu23/Academix) | 9 | 跨 5 源统一搜索、智能 ID 解析、BibTeX 批量导出 | 补充外部学术源聚合策略 |
| [Scholar MCP](https://github.com/pvliesdonk/scholar-mcp) | — | 论文+专利+图书+标准四域搜索，27 个工具 | 未来可扩展专利/图书/标准搜索 |

---

## 2. 总体开发目标

### 2.1 短期目标

让 skill 更稳定地完成以下任务：

- 根据自然语言问题检索 Zotero 文献；
- 根据草稿段落拆解主张并匹配证据；
- 为论文段落推荐可追溯的 Zotero 引文；
- 明确标出 Zotero 中没有证据支持的主张；
- 避免虚构文献、虚构 DOI、虚构结论。

### 2.2 中期目标

将 skill 扩展为科研写作中的 Zotero evidence assistant：

- 支持文献综述证据矩阵；
- 支持方法学、机制、流行病学、临床研究分类；
- 支持引用核查和引用替换建议；
- 支持 collection/tag 驱动的专题检索；
- 支持 notes/annotations 驱动的精读材料提取。

### 2.3 长期目标

形成完整的 Zotero MCP 科研工作流技能集：

```text
zotero-skills/
├── zotero-evidence-review/          # 文献检索与证据链
├── zotero-citation-audit/      # 引用核查与引文替换
├── zotero-library-manager/     # 标签、分类、重复项、导入管理
├── zotero-note-reader/         # 笔记、标注、全文精读
└── zotero-review-builder/      # 综述矩阵与研究空白分析
```

---

## 3. 建议一：补充工具选择决策树

### 3.1 目的

当前 skill 描述了“优先语义搜索”，但没有明确不同 Zotero MCP 工具的适用边界。建议增加 `Tool Selection` 章节。

### 3.2 推荐内容

```markdown
## Tool Selection

- For conceptual literature discovery, use `zotero_semantic_search` first.
- For exact title, DOI, PMID, author, or keyword queries, use `zotero_search_items` or `zotero_advanced_search`.
- For citation-key lookup, use `zotero_search_by_citation_key`.
- For metadata, abstracts, BibTeX, or JSON export, use `zotero_get_item_metadata`.
- For full text, use `zotero_get_item_fulltext` or `zotero_read_pdf_pages`.
- For annotations and reading notes, use `zotero_get_annotations` and `zotero_get_notes`.
- For collection-level search, use `zotero_get_collections`, `zotero_search_collections`, and `zotero_get_collection_items`.
- For semantic database status, use `zotero_get_search_database_status`.
- For semantic database update, use `zotero_update_search_database` only when needed.
```

### 3.3 优先级

高。

### 3.4 预期收益

- 减少模型误用工具；
- 提高检索准确性；
- 方便用户理解 skill 的行为逻辑；
- 更适合 ZCode/OpenCode 多环境使用。

---

## 4. 建议二：增加安全规则

### 4.1 目的

Zotero MCP 不仅能搜索，也能添加、修改、删除文献、笔记、标注和标签。skill 应明确安全边界。

### 4.2 推荐内容

```markdown
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
```

### 4.3 优先级

高。

### 4.4 预期收益

- 防止误删文献；
- 防止批量修改造成文献库混乱；
- 强化科研写作中的引用可信度。

---

## 5. 建议三：标准化检索输出格式

### 5.1 目的

当前输出格式已有标题、作者、年份、期刊、相似度和 Zotero link。建议补充更多可追溯字段。

### 5.2 推荐格式

```markdown
## Zotero Search Results

### 1. Title
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

### 5.3 优先级

高。

### 5.4 预期收益

- 检索结果更容易复核；
- 方便后续写作、引用和文献矩阵整理；
- 减少“看似相关但不能引用”的结果。

---

## 6. 建议四：增强证据链模块

### 6.1 目的

当前证据链已经能区分 supporting、contrasting 和 context。建议进一步细分证据角色。

### 6.2 推荐证据类型

```markdown
## Evidence Types

- **Direct support**: directly supports the claim.
- **Indirect support**: supports part of the mechanism or context.
- **Contrasting evidence**: reports inconsistent or opposite findings.
- **Mechanistic evidence**: explains biological, behavioral, or methodological mechanisms.
- **Methodological evidence**: supports the design, measurement, or analytical method.
- **Background evidence**: useful for introduction or broad framing.
- **Gap**: no adequate Zotero evidence found.
```

### 6.3 推荐输出格式

```markdown
## Evidence Chain

### Claim 1: ...

**Claim type**: causal / association / mechanism / background / method

**Evidence found**:
- ✅ Direct support: Author et al. (Year), Title, ItemKey, DOI
- 🧬 Mechanistic evidence: Author et al. (Year), Title, ItemKey, DOI
- 🔄 Contrasting evidence: Author et al. (Year), Title, ItemKey, DOI

**Assessment**:
- Evidence strength: strong / moderate / weak / insufficient
- Suggested wording: ...
- Citation gap: yes / no
```

### 6.4 优先级

中高。

### 6.5 预期收益

- 更适合论文 discussion 和 introduction 写作；
- 能避免把间接证据写成直接因果证据；
- 更适合系统综述、叙述性综述和 grant writing。

---

## 7. 建议五：增加中文科研写作规则

### 7.1 目的

该 skill 的主要使用场景包含中文科研写作，应明确中文输出规范。

### 7.2 推荐内容

```markdown
## Chinese Academic Writing Rules

When responding in Chinese:

- Keep article titles, journal names, author names, DOI, PMID, and item keys in English.
- Do not translate official paper titles unless the user asks.
- Distinguish association, causation, mediation, prediction, and mechanism.
- Use cautious wording when evidence is indirect, observational, or inconsistent.
- Do not use a Zotero item as evidence unless its metadata, abstract, full text, note, or annotation has been inspected.
- Clearly mark whether each citation is for background, method, mechanism, or direct empirical evidence.
```

### 7.3 优先级

中高。

### 7.4 预期收益

- 更适合中文论文、中文基金标书和中文博士论文写作；
- 减少因果夸大；
- 保持中英文文献信息的一致性。

---

## 8. 建议六：加入 citation audit 工作流

### 8.1 目的

除了找文献，科研写作中非常常见的需求是“检查这句话后面的引用是否真的支持这句话”。

### 8.2 推荐新增章节

```markdown
## Citation Audit Workflow

When the user provides a sentence or paragraph with citations:

1. Extract each cited claim.
2. Identify the citation attached to each claim.
3. Retrieve Zotero metadata and abstract/full text when possible.
4. Judge whether the citation supports the claim.
5. Classify the match:
   - fully supports;
   - partially supports;
   - background only;
   - does not support;
   - cannot verify from available metadata.
6. Suggest replacement or additional Zotero citations if needed.
```

### 8.3 推荐输出

```markdown
## Citation Audit

| Claim | Citation | Support level | Issue | Suggested fix |
|---|---|---|---|---|
| ... | Author 2020 | Partial | supports association, not causation | weaken wording or add mechanistic source |
```

### 8.4 优先级

中。

### 8.5 预期收益

- 提高论文引用准确性；
- 降低审稿人质疑“引用不支持论断”的风险；
- 可与 citation-verifier、evidence-driven-writing 等技能形成互补。

---

## 9. 建议七：增加 collection/tag 驱动的专题检索

### 9.1 目的

很多 Zotero 用户会用 collection 和 tag 管理专题。skill 可以更主动利用这些结构。

### 9.2 推荐新增内容

```markdown
## Collection and Tag Search

Use collection or tag filters when:

- the user names a specific research project;
- the user asks for papers from a known Zotero folder;
- the query is broad and the user's library is large;
- the user asks for reviewed, important, included, excluded, or to-read items.

Suggested workflow:

1. Search collections by name.
2. Retrieve collection items.
3. Search within the collection if needed.
4. Combine semantic relevance with collection membership.
```

### 9.3 优先级

中。

### 9.4 预期收益

- 更适合大型 Zotero 文献库；
- 能利用用户已有的知识组织结构；
- 对系统综述、课题文献库、博士论文专题库很有用。

---

## 10. 建议八：增加 semantic index 诊断流程

### 10.1 目的

语义搜索依赖索引，用户常遇到“新文献搜不到”“语义搜索无结果”“全文没有被索引”等问题。

### 10.2 推荐新增内容

```markdown
## Semantic Index Diagnostics

If semantic search returns poor or no results:

1. Check semantic database status.
2. Ask whether new items were recently added.
3. Recommend incremental update: `zotero-mcp update-db`.
4. If full-text evidence is required, recommend: `zotero-mcp update-db --fulltext`.
5. If the embedding model changed or the database is corrupted, recommend force rebuild only after confirmation.
```

### 10.3 优先级

中。

### 10.4 预期收益

- 降低用户排障成本；
- 提高语义检索召回率；
- 避免不必要的 force rebuild。

---

## 11. 建议九：把 OpenCode 指南与 Skill 行为分离

### 11.1 目的

`Zotero_MCP_OpenCode_Guide.md` 是很好的用户手册，但 `SKILL.md` 应更聚焦 agent 行为规则，不宜承担过多安装说明。

### 11.2 推荐分工

```text
README.md
  - 项目介绍
  - 安装方式
  - 快速开始
  - 示例

Zotero_MCP_OpenCode_Guide.md
  - OpenCode/ZCode MCP 配置
  - zotero-mcp 安装
  - CLI 使用
  - 常见问题

zotero-evidence-review/SKILL.md
  - skill 触发条件
  - 工具选择
  - 检索工作流
  - 证据链工作流
  - 输出格式
  - 安全规则
```

### 11.3 优先级

中。

---

## 12. 建议十：增加测试用例与示例提示词

### 12.1 目的

skill 迭代后需要有稳定的人工测试样例。

### 12.2 推荐新增文件

```text
examples/
├── search-prompts.md
├── evidence-chain-prompts.md
├── citation-audit-prompts.md
└── expected-output-templates.md
```

### 12.3 示例测试用例

```markdown
## Test 1: Conceptual semantic search
Prompt: 搜索 Zotero 中关于 PCOS、久坐行为和炎症的研究，列出最相关的 5 篇。
Expected: uses semantic search, returns item keys, DOI, relevance explanation.

## Test 2: Exact DOI lookup
Prompt: 查找 DOI 为 10.xxxx/xxxxx 的文献并导出 BibTeX。
Expected: uses exact search or metadata, not semantic search.

## Test 3: Evidence chain
Prompt: 久坐行为通过慢性炎症促进胰岛素抵抗，请帮我找证据链。
Expected: separates sedentary behavior → inflammation, inflammation → insulin resistance, insulin resistance → PCOS.

## Test 4: No evidence found
Prompt: 查找 Zotero 中关于某个不存在主题的文献。
Expected: clearly says no matching Zotero evidence found and suggests external search query.
```

### 12.4 优先级

中低。

---

## 13. 建议十一：增加 PDF 全文引用验证协议

### 13.1 目的

当前 Citation Audit 仅做元数据级核对，但科研写作中最严格的验证需求是"确认某句话是否真的由某篇文献支持"。参考 KellanLow/Zotero-MCP-Usage 的零容忍协议，增加 PDF 全文逐页验证模式。

### 13.2 推荐内容

```markdown
## Strict Citation Verification

当用户要求验证具体引用准确性时，启动此模式：

### 预检
1. 估算 Token 预算：Pages × 700 + 1000
2. 检查剩余 Token（< 50k 时警告）
3. 检查 Zotero 全文是否可用

### 逐页验证（禁止跳过）
1. 提取完整 PDF 到临时文件
2. 按 250-300 行分块顺序阅读
3. 记录每处引用的精确行号和原文
4. 验证数值数据（N=X, p<0.05）
5. 对照 Zotero 元数据交叉核对

### 自检清单
- [ ] 已读取从第一页到最后一页的全部内容
- [ ] 已定位 References 部分（证明读完全文）
- [ ] 已记录所有引用的行号
- [ ] 已验证数值数据的准确性
- [ ] Token 未超预算
```

### 13.3 优先级

中高。

### 13.4 预期收益

- 杜绝"引用与声明不符"的审稿风险；
- 适合 journal club、审稿、meta-analysis 场景；
- 提供清晰的自检和反作弊机制。

---

## 14. 建议十二：增加中文文献结构化核查流程

### 14.1 目的

当前计划已有 Chinese Academic Writing Rules，但无具体可执行的核查流程。参考 yipng05-max/literature-verifier，将中文核查从"规则"升级为"流程"。

### 14.2 推荐内容

```markdown
## Chinese Literature Verification

### 优先方法：知网 CDP 直接检索
需要 Chrome MCP 工具可用时：

1. 打开知网高级检索页面 `kns.cnki.net/kns8s/AdvSearch`
2. 处理可能出现的验证码（截图确认）
3. 输入论文精确标题检索
4. 读取结果页结构化数据
5. 逐项比对：标题 / 作者 / 期刊 / 年份
6. 判定：Confirmed / Likely Real / Metadata Error

### 备选方法：WebSearch 多重交叉验证
当 CDP 不可用时，执行以下全部搜索：

1. 精确标题搜索 `"<完整论文标题>"`
2. 标题+作者搜索 `<标题> <作者>`
3. 知网定向 `"<标题>" site:cnki.net`
4. 万方定向 `"<标题>" site:wanfangdata.com.cn`
5. 百度学术定向 `"<标题>" site:xueshu.baidu.com`

### 禁止行为
- ❌ 以"需知网核实"搪塞——必须给出明确判定
- ❌ 中文无 DOI 即判定为虚构
- ❌ 仅搜索一个来源即下结论
```

### 14.3 优先级

中高。

### 14.4 预期收益

- 中文文献核查从"建议"变为可执行流程；
- 减少"无法查证"类搪塞回复；
- 覆盖中文期刊、图书、学位论文、政策文件。

---

## 15. 建议十三：增加外部学术源补充检索策略

### 15.1 目的

Zotero 检索不到时不停止工作，而是利用外部免费学术 MCP Server 和公开 API 补全。

### 15.2 推荐内容

```markdown
## External Source Fallback

当 Zotero 检索结果不足时，建议启用以下免费 MCP Server：

| MCP Server | 覆盖 | API Key | 适用场景 |
|-----------|------|---------|---------|
| crossref-academic-mcp-server | Crossref + OpenAlex + Semantic Scholar | 无需 | DOI解析、引用网络、作者画像 |
| paper-search-mcp | arXiv + PubMed + bioRxiv | 无需 | 预印本和生物医学文献 |
| academix | OpenAlex + DBLP + Semantic Scholar + arXiv + CrossRef | 无需 | 计算机科学、多源聚合 |

### 流程
1. 先用 Zotero 内部检索
2. 不足时启动外部 MCP fallback
3. 找到后询问用户是否要加入 Zotero
4. 所有外部结果标注来源，不得与 Zotero 结果混淆
```

### 15.3 优先级

中。

### 15.4 预期收益

- 弥补 Zotero 库覆盖的不足；
- 用户不需手动去 Google Scholar 补搜；
- 为后续"zotero-review-builder"提供外部数据源。

---

## 16. 建议十四：增加系统综述 PRISMA 工作流

### 16.1 目的

当用户进行系统综述或文献综述时，需要标准化的 PRISMA 流程和多源证据等级评估。

### 16.2 推荐内容

```markdown
## Systematic Review Workflow

适用于系统综述、scoping review、narrative review。

### 搜索阶段
1. Zotero + 外部 MCP 跨库搜索
2. DOI/标题去重
3. 标题筛选 → 摘要筛选 → 全文筛选

### 证据等级标注
| 等级 | 标准 |
|------|------|
| High | 多项 RCT 或高质量 Meta 分析 |
| Moderate | ≥1 项 RCT + 观察性研究一致 |
| Low | 仅观察性研究或结果不一致 |
| Very Low | 专家意见、病例报告、机制推断 |

### 输出：PRISMA 流程表
```
初始检索: n = X
├─ 去重后: n = Y
├─ 标题筛选后: n = Z
├─ 全文筛选后: n = A
└─ 最终纳入: n = B
```
```

### 16.3 优先级

中。

### 16.4 预期收益

- 填补从"证据链"到"系统综述"的流程缺失；
- 与 K-Dense-AI 的 literature-review skill 互补；
- 更适合博士论文和 grant 申请。

---

## 17. 建议开发路线图

### Phase 1：稳定性与安全性

预计工作量：0.5–1 天。

任务：

- [ ] 在 `SKILL.md` 增加 Tool Selection 章节；
- [ ] 增加 Safety Rules；
- [ ] 增加 Never fabricate citations 规则；
- [ ] 标准化 Search Results 输出格式；
- [ ] 标准化 Evidence Chain 输出格式。

验收标准：

- skill 明确知道不同 Zotero MCP 工具的使用场景；
- 所有删除、合并、批量修改类操作都要求确认；
- 所有检索结果均包含 Zotero item key 或明确说明缺失；
- 未检索到文献时不会编造引用。

### Phase 2：科研写作增强

预计工作量：1–2 天。

任务：

- [ ] 增加 Chinese Academic Writing Rules；
- [ ] 增加 Evidence Types；
- [ ] 增加 Citation Audit Workflow；
- [ ] 增加写作建议中的因果弱化规则；
- [ ] 增加"证据强度"标注：strong / moderate / weak / insufficient。

验收标准：

- 能区分 association、causation、mechanism、prediction；
- 能指出引用是否只是背景证据；
- 能建议更谨慎的中文学术表述。

### Phase 3：文献库组织能力

预计工作量：1–2 天。

任务：

- [ ] 增加 collection/tag 检索流程；
- [ ] 增加 notes/annotations 读取流程；
- [ ] 增加 semantic index diagnostics；
- [ ] 增加"新文献搜不到"的排障说明。

验收标准：

- 能根据 collection 或 tag 限定专题文献；
- 能从笔记和标注中提取证据；
- 能诊断语义索引问题并给出安全建议。

### Phase 4：示例与测试

预计工作量：0.5–1 天。

任务：

- [ ] 新建 `examples/`；
- [ ] 添加 10–20 个常用提示词；
- [ ] 添加期望输出模板；
- [ ] 在 README 中增加 examples 链接。

验收标准：

- 新用户能通过示例快速理解 skill；
- 开发者能用样例测试 skill 行为是否退化。

### Phase 5：引用验证与外部源集成

预计工作量：1–2 天。

任务：

- [ ] 增加 Strict Citation Verification 协议（PDF 逐页验证）；
- [ ] 增加 Chinese Literature Verification 流程（CDP + WebSearch）；
- [ ] 增加 External Source Fallback 策略；
- [ ] 增加 Systematic Review Workflow（PRISMA）；
- [ ] 在 README 中列出推荐的配套 MCP Server。

验收标准：

- 能对引用做逐行原文验证；
- 中文文献有明确的核查路径和判定体系；
- Zotero 检索不足时能建议外部源；
- 提供系统综述的标准工作流模板。

---

## 18. 推荐的下一版 `SKILL.md` 结构

```markdown
---
name: zotero-evidence-review
description: Search, analyze, and verify citations in your Zotero library using semantic search, evidence-chain extraction, full-text citation verification, and writing suggestions grounded in your collection. Requires Zotero MCP.
license: MIT
compatibility: opencode,zcode
metadata:
  workflow: academic-research
  requires: zotero-mcp
  version: 2.0.0
---

# Zotero Evidence Review Skill

## When to Use
## Core Principles
## Tool Selection
## Safety Rules
## Semantic + Structured Search Workflow
## Evidence Chain Workflow
## Citation Audit Workflow
## Strict Citation Verification
## Citation-Grounded Writing Suggestions
## Collection and Tag Search
## Notes and Annotations
## Chinese Literature Verification
## Chinese Academic Writing Rules
## External Source Fallback
## Systematic Review Workflow
## Semantic Index Diagnostics
## Output Formats
## Usage Examples
```

---

## 19. 立即可执行的最小修改清单

建议下一次提交优先完成以下 7 个修改（比原计划增加 2 项）：

1. 在 `zotero-evidence-review/SKILL.md` 增加 `Tool Selection`。
2. 在 `zotero-evidence-review/SKILL.md` 增加 `Safety Rules`。
3. 在 `zotero-evidence-review/SKILL.md` 增加 `Never fabricate citations`。
4. 将检索输出格式扩展为包含 DOI、item key、evidence role、why relevant。
5. 将证据链输出扩展为包含 evidence strength 和 suggested wording。
6. 增加 `Strict Citation Verification` 章节（PDF 逐页验证协议）。
7. 增加 `Chinese Literature Verification` 章节（CDP + WebSearch 流程）。

这 7 项完成后，skill 的可靠性和科研写作可用性会明显提升。

### 后续迭代（上述完成后）

8. 增加 `External Source Fallback` 策略。
9. 增加 `Systematic Review Workflow`（PRISMA）。
10. 在 README 中列出推荐的配套 MCP Server。
11. 在 frontmatter 中增加 `version: 2.0.0`。
