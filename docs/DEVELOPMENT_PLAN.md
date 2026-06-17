# zotero-evidence-review 开发方案与计划

> 基于 v2.0.0 现状分析，共 6 个改进阶段，按优先级排列。
> 每阶段包含：目标、具体改动、可直接用于修改 SKILL.md 的 AI 提示词。

---

## 阶段一：入口路由（Intent Detection）+ 模块2/3合并重设计

**优先级**: 🔴 高

### 1A. 路由简化

原模块2（证据链）和模块3（写作建议）**合并为一个入口**：用户粘贴段落即触发，无需区分意图。

在 `## Tool Selection` 之前插入路由章节，意图只有 **4 类**：

| 用户输入特征 | 自动路由至 |
|-------------|-----------|
| 关键词 / 概念 / 问句 | 模块 1：语义+结构搜索 |
| 粘贴段落（无论说"找证据"还是"补引用"） | 模块 2：段落证据与引文分析（合并） |
| "验证"、"核实" + 具体引用+主张 | 模块 3：精确核实 |
| "库状态"、"健康检查" | 模块 4：库健康度（后续阶段） |
| 意图不明 | 输出编号菜单（1–4），用户选择 |

---

### 1B. 合并后的模块 2 设计：段落证据与引文分析

**核心原则**：一次搜索，两层输出。不重复搜 Zotero，不让用户选模式。

#### 流程

```
用户粘贴段落
    │
    ├─ Step 1: 句子拆分 + 主张提取（每句 1-2 个核心主张）
    │
    ├─ Step 2: 批量构造搜索查询（所有主张合并为一次搜索）
    │          semantic_search + keyword fallback
    │
    ├─ Step 3: 两层输出（共用同一批搜索结果）
    │   ├─ 层A（证据质量）：每个主张 → 支持强度 / gap 标注
    │   └─ 层B（引文推荐）：每句话 → 推荐引哪篇
    │
    ├─ Step 4: diff 视图（段落修改版，标注新增引用位置）
    │
    └─ Step 5: Gap 汇总 → 询问是否启动外部搜索
```

#### 输出格式

```markdown
## 段落分析：<主题短语>

### Refs（元数据唯一出现一次）
- `KEY` — Author (Year). *Title*. *Journal*. DOI.

### 层A：主张-证据矩阵
| # | 主张 | 最佳引文 | 强度 | Gap? |
|---|------|---------|------|------|
| 1 | X与Y相关 | Wang 2022 (KEY) | 强 | 否 |
| 2 | Z导致W | — | — | ⚠️ 是 |

### 层B：逐句引文推荐
| 句子（前15字） | 推荐引文 | 引用理由 |
|--------------|---------|---------|
| "慢性炎症通过…" | Wang 2022 (KEY) | 直接证据 |

### 修改版段落（diff）
> 原文改动：~~删除~~ / **新增**
> 改动摘要：+2引用，改写1处措辞

### Gap 与外部搜索
- ⚠️ 主张2 无库内证据 → 建议查询：`"Z causes W" mechanism`
- 是否启动外部搜索？(y/n)
```

### AI 提示词

```
你是 zotero-evidence-review skill 的维护者。

请对 SKILL.md 做以下两项修改：

【修改1】在 "## Tool Selection" 之前新增 "## 0. Intent Detection" 章节：
- 定义 4 类意图：search（关键词/概念）/ paragraph（粘贴段落）/ verify（核实引用）/ health（库状态）
- 粘贴段落统一路由至模块2，不区分"找证据"和"补引用"
- 意图不明时输出编号菜单（1–4）

【修改2】将 "## 2. Evidence Chain Extraction" 和 "## 3. Citation-Grounded Writing Suggestions"
合并替换为一个新章节 "## 2. Paragraph Evidence & Citation Analysis"：
- 流程：句子拆分 → 批量搜索（一次）→ 两层输出（证据质量 + 逐句引文）
- 输出包含：Refs块 / 主张-证据矩阵 / 逐句引文推荐 / diff段落 / Gap汇总
- diff格式：~~删除~~ 标删除，**粗体** 标新增，末尾注明改动摘要
- Gap汇总后询问是否启动外部搜索（对接 "## External Source Fallback"）
- 原模块3的"6类建议"合并进逐句引文推荐列的"引用理由"列，不单独展示
- 后续章节编号相应更新：原4→3，原5→4，原6→5，原7→6

输出要求：输出修改后的完整两个章节文本（## 0. Intent Detection 和 ## 2. Paragraph Evidence & Citation Analysis）。
```

---

## 阶段二：Gap → 外部搜索自动衔接

**优先级**: 🔴 高  
**目标**: Evidence Chain 发现 gap 后，不仅提示"建议搜索 X"，而是直接衔接模块 7（外部回退），并询问是否将结果加入 Zotero。

### 具体改动

在 `## 2. Evidence Chain Extraction` 的输出格式后追加 **Gap 处理子流程**：

```
Gap 自动处理流程：
1. 统计所有 gap 主张
2. 对每个 gap 构造外部搜索查询（英文 + 中文双语）
3. 提示用户："发现 N 处证据缺口，是否启动外部文献搜索？(y/n)"
4. 若用户确认：调用 crossref/paper-search MCP，返回 top-3 外部结果
5. 询问："是否将以上结果添加到 Zotero？"
```

### AI 提示词

```
你是 zotero-evidence-review skill 的维护者。

请修改 SKILL.md 中 "## 2. Evidence Chain Extraction" 章节，在现有输出格式后面，追加一个子章节 "### Gap Handling"。

该子章节需要描述以下流程：
1. 当 Evidence Chain 结果中存在 Gap=yes 的行时，自动进入 Gap 处理流程
2. 为每个 gap 构造英文搜索查询（query 字段），优先使用 MeSH 术语
3. 向用户展示 gap 汇总，并询问是否启动外部搜索（参考 "## 7. External Source Fallback" 中的 MCP 工具）
4. 外部搜索结果展示后，询问用户是否通过 zotero_add_by_doi 或 zotero_add_by_url 加入 Zotero
5. 安全规则：添加操作需要用户确认

输出要求：只输出新增的 "### Gap Handling" 子章节文本。
```

---

## 阶段三：写作建议 Diff 视图

**优先级**: 🟡 中  
**目标**: 在"写作建议"输出的 `Suggested revised paragraph` 中，用 `~~删除~~` / `**新增**` 标注具体改动，让用户一眼看出变化。

### 具体改动

修改模块 3 的 `Canonical "Paragraph Citation Review" Layout` 中 `### 5. Suggested revised paragraph` 的格式要求：

```markdown
### 5. Suggested revised paragraph

<!-- diff 格式规则：
  - 删除的词/短语：用 ~~strikethrough~~ 标注
  - 新增的词/短语：用 **bold** 标注  
  - 未改动部分保持原样
  - 段落末尾附 "改动摘要"：列出改动类型和数量
-->
```

### AI 提示词

```
你是 zotero-evidence-review skill 的维护者。

请修改 SKILL.md 中 "## 3. Citation-Grounded Writing Suggestions" 章节里
"### Canonical 'Paragraph Citation Review' Layout" 的 "### 5. Suggested revised paragraph" 部分。

修改要求：
1. 在该子节开头加入 diff 格式说明：
   - 删除内容用 ~~删除~~ 标注
   - 新增内容用 **新增** 标注
   - 未改动内容保持原样
2. 在段落末尾要求输出"改动摘要"：格式为 "改动：+N词/-M词，修改原因：[简短说明]"
3. 加入示例，展示 diff 格式的实际效果

输出要求：只输出修改后的 "### 5. Suggested revised paragraph" 子节内容。
```

---

## 阶段四：核实协议统一

**优先级**: 🟡 中  
**目标**: 将英文核实（模块4）和中文核实（模块5）合并为统一的"核实协议"，根据文献语言自动选择路径，避免用户手动判断。

### 具体改动

将现有模块 4 和模块 5 替换为统一的 `## 4. Citation Verification Protocol`：

```
统一核实协议：
├── 语言检测：从 Zotero 元数据/摘要判断文献语言
│   ├── 英文 → Full-text PDF path（原模块4流程）
│   └── 中文 → CNKI CDP / WebSearch path（原模块5流程）
├── 共用：preflight token budget 检查
└── 共用：统一输出格式（Verification Report 表格）
```

### AI 提示词

```
你是 zotero-evidence-review skill 的维护者。

请将 SKILL.md 中的 "## 4. Strict Citation Verification" 和 "## 5. Chinese Literature Verification"
合并为一个新章节 "## 4. Citation Verification Protocol"。

合并要求：
1. 新章节开头加入"语言检测"步骤：通过 zotero_get_item_metadata 获取元数据，
   根据 language 字段或标题/摘要语言判断文献语种
2. 英文文献走原模块4的 PDF full-text 路径
3. 中文文献走原模块5的 CNKI CDP / WebSearch 路径
4. Preflight（token budget 检查）和输出格式（Verification Report 表格）两个模块共用，
   不重复出现
5. 删除原来的模块4和模块5，后续模块编号相应更新（原6→5，原7→6）

输出要求：输出完整的新 "## 4. Citation Verification Protocol" 章节文本。
```

---

## 阶段五：库健康度 Preflight

**优先级**: 🟢 低  
**目标**: 新增 `## 0.5 Library Health Check` 模式（或作为入口路由的一个选项），让用户一键了解 Zotero 库状态。

### 具体检查项

| 检查项 | 使用工具 | 输出 |
|--------|---------|------|
| 语义索引状态 | `zotero_get_search_database_status` | 已索引条目数 / 最后更新时间 |
| PDF 覆盖率 | `zotero_advanced_search` (has attachment) | 有PDF/总条目 百分比 |
| 重复条目 | `zotero_find_duplicates` | 重复组数量 |
| 无摘要条目 | `zotero_advanced_search` (abstract is empty) | 数量 + 建议补充 |

### AI 提示词

```
你是 zotero-evidence-review skill 的维护者。

请在 SKILL.md 中，紧跟 "## 0. Intent Detection" 章节之后，
新增一个章节 "## 0.5 Library Health Check"。

该章节需要：
1. 描述何时触发（用户输入包含"库状态"、"健康检查"、"preflight"、"索引状态"）
2. 列出 4 项检查内容（语义索引、PDF覆盖率、重复条目、无摘要条目），
   以及每项对应的 Zotero MCP 工具调用方式
3. 定义输出格式：一个简洁的健康度摘要表格，含"状态"（✅/⚠️/❌）和"建议操作"列
4. 添加安全规则：健康检查只读，不自动执行修复操作，修复需用户确认

输出要求：只输出新增章节的 Markdown 文本。
```

---

## 阶段六：输出模板提取（重构）

**优先级**: 🟢 低  
**目标**: 将各模块重复出现的输出格式抽取为 `## Appendix: Output Templates`，减少 SKILL.md 冗余，便于维护。

### 可复用模板清单

| 模板名 | 目前出现位置 |
|--------|------------|
| `REFS_BLOCK` | 模块1、模块3均有定义 |
| `CLAIM_EVIDENCE_MATRIX` | 模块2输出格式 |
| `WRITING_SUGGESTIONS_TABLE` | 模块3输出格式 |
| `VERIFICATION_REPORT` | 模块4、模块5均有定义 |

### AI 提示词

```
你是 zotero-evidence-review skill 的维护者。

请对 SKILL.md 进行以下重构：
1. 在文件末尾新增 "## Appendix: Output Templates" 章节
2. 将以下 4 个在正文中重复出现的输出格式抽取为命名模板：
   - REFS_BLOCK（引用块，出现在模块1和模块3）
   - CLAIM_EVIDENCE_MATRIX（主张-证据矩阵，模块2）
   - WRITING_SUGGESTIONS_TABLE（写作建议表格，模块3）
   - VERIFICATION_REPORT（核实报告，模块4/5）
3. 在正文原来定义这些格式的位置，替换为引用说明，例如：
   "输出格式见 Appendix: REFS_BLOCK 模板"
4. 不改变任何现有功能描述或规则

输出要求：输出重构后的完整 SKILL.md 内容（分段输出，每次输出约 100 行）。
```

---

## 实施时间线建议

```
Week 1-2   Phase 1: 入口路由
Week 2-3   Phase 2: Gap 自动衔接
Week 3-4   Phase 3: Diff 视图
Week 4-5   Phase 4: 核实协议统一
Week 5     Phase 5: 库健康度
Week 6     Phase 6: 重构/模板提取
```

---

## 版本规划

| 版本 | 包含阶段 | 里程碑 |
|------|---------|-------|
| v2.1.0 | Phase 1 + 2 | 智能路由 + gap闭环 |
| v2.2.0 | Phase 3 + 4 | 写作增强 + 统一核实 |
| v3.0.0 | Phase 5 + 6 | 库管理 + 全面重构 |
