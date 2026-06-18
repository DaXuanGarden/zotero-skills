# 📚 Zotero Skills

> 面向 OpenCode / ZCode 的 Zotero 文献证据审查技能：让 AI 助手在你的 Zotero 文献库中检索、分析、核实引用，并给出可追溯的写作建议。

![OpenCode](https://img.shields.io/badge/OpenCode-MCP-0175C2)
![ZCode](https://img.shields.io/badge/ZCode-Skill-6f42c1)
![Zotero MCP](https://img.shields.io/badge/Zotero-MCP-CC2936)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 1. 项目概览

本仓库提供一个核心 skill：`zotero-evidence-review`。它通过 Zotero MCP 连接本地 Zotero 文献库，支持从“找文献”到完整的 **Paragraph Citation Package Workflow**（段落 → 主张拆解 → Zotero 本地检索 → PubMed 条件扩展 → 引文放置 → Markdown 证据报告 + EndNote RIS）再到“逐条核实引用是否真的支持主张”的证据审查工作流。

推荐使用路径：先安装并配置 Zotero MCP → 构建语义索引 → 直接在 ZCode / OpenCode 中用自然语言触发 skill → 默认得到一份 Markdown evidence report 和一份 RIS；如果只想聊天查看结果，可明确说 `只在聊天输出` 或 `不要生成文件`。

| 项目 | 当前状态 |
|---|---|
| Skill | `zotero-evidence-review` |
| 当前版本 | `2.1.1` |
| 兼容性 | OpenCode / ZCode |
| 主要依赖 | Zotero 7+、zotero-mcp、Python 3.10+；可选 PubMed MCP（推荐 PancrePal） |
| 安装目标 | ZCode 全局、OpenCode 全局、项目级 `.opencode/skills` |
| 默认安全策略 | 健康检查只读；删除、批量修改、合并重复项等操作必须先确认 |

---

## 2. 核心能力

| 能力 | 说明 |
|---|---|
| **Intent Detection** | 根据用户输入自动判断是文献检索、段落证据分析、引用核实，还是库健康检查。 |
| **Library Health Check** | 只读检查语义索引、PDF 覆盖、重复条目、缺失摘要等状态；不可用项目明确标记为 `⚠️`。 |
| **Semantic + Structured Search** | 优先语义搜索概念相近文献，并结合标题、作者、关键词、DOI、PMID、年份等结构化检索兜底。 |
| **Collection and Tag Search** | 支持按 Zotero collection、tag、分类范围缩小检索。 |
| **Paragraph Citation Package Workflow** | 段落补引用默认是一个完整工作流：claim extraction → Zotero local search → evidence matrix / citation placement / diff paragraph → automatic PubMed expansion when available → Markdown report + EndNote RIS。 |
| **Zotero + PubMed Dual-MCP Workflow** | Zotero MCP 负责本地库、PDF/笔记/collection/语义检索；PubMed MCP 负责生物医学外部扩展、PMID 元数据、related/review discovery、OA/full-text triage 与参考文献标准化。 |
| **Citation Verification Protocol** | 针对具体文献和具体主张读取元数据与全文，判断 fully supported / partially supported / contradicted / not addressed。 |
| **Chinese Academic Writing Rules** | 面向中文学术写作，保留原意、避免虚构引用，输出可追踪的润色与补引建议。 |
| **External Source Fallback** | Zotero 库证据不足时，可在外部 MCP 工具已配置的前提下辅助扩展；未配置时只给出可复制检索式。 |
| **Evidence Package Export** | 作为 Paragraph Citation Package Workflow 的导出阶段，生成两个可复用文件：Markdown 证据报告与可导入 EndNote 的 RIS 参考文献文件。 |

---

## 3. 5 分钟快速安装

### 3.1 前置条件

请先确认：

- 已安装并打开 **Zotero 7+**。
- Zotero 中已启用本地访问：Zotero 设置 → 高级 → 允许其他应用程序访问 Zotero。
- 已安装 **Python 3.10+**。
- 已安装 OpenCode 或 ZCode。
- 已安装并配置 `zotero-mcp`（见 [第 5 节](#5-配置-zotero-mcp)）。
- 如果需要 PubMed 扩展、PMID 标准化、related/review discovery 或 OA 全文检测，另行配置 PubMed MCP（见 [PubMed Expansion](#83-pubmed-expansion) 和 [`docs/PANCREPAL_PUBMED_MCP_GUIDE.md`](./docs/PANCREPAL_PUBMED_MCP_GUIDE.md)）。

### 3.2 克隆仓库并安装到 ZCode（推荐）

```bash
git clone https://github.com/DaXuanGarden/zotero-skills.git
cd zotero-skills

# 安装/更新到 ZCode 全局 skill 目录，并在覆盖前备份旧版本
scripts/install-skill.sh --target zcode --backup

# 验证 skill 文件结构
scripts/validate-skill.py
```

`scripts/validate-skill.py` 是静态校验工具：它检查 `zotero-evidence-review/SKILL.md` 的 frontmatter、依赖声明（`metadata.requires: zotero-mcp` / `metadata.optional: pubmed-mcp`）、章节、输出模板、Evidence Package/RIS 约束和外部工具安全防护说明；它不会连接 Zotero、不会执行 PubMed 检索，也不会验证 README 的自然语言描述。

### 3.3 静态校验 vs 运行时 MCP 就绪

静态校验通过只说明 skill 文本结构正确，不等于当前 Agent IDE 会话已经能调用 Zotero / PubMed。真正执行工作流前，请按下面的只读 checklist 快速确认：

| 检查项 | 期望状态 | 不满足时的正确行为 |
|---|---|---|
| Zotero MCP 工具可见 | 当前会话能看到 Zotero search / metadata / fulltext / children 等工具 | 不声称已完成 Zotero 本地检索；先修复 MCP 配置 |
| Zotero 语义索引 / fulltext 可用 | 可读取 `zotero_get_search_database_status`，必要时能访问 PDF/fulltext | 报告索引或全文限制；不要虚构全文核查 |
| PubMed MCP 工具可见（可选） | 当前会话能看到 `pubmed_search`、`pubmed_get_details`、`pubmed_extract_info`、`pubmed_find_related` 等 PubMed/NCBI 工具 | 报告 `PubMed: ⚠️ Tool unavailable; search not executed`，并给出可复制 query |
| PubMed 已实际运行且元数据已检查 | PubMed search 有返回，候选 PMID 已用详情/抽取工具检查 | 只有此时才能写 `PubMed: Completed` 或生成 PubMed-only RIS |

换句话说：validator 是仓库侧 guardrail；MCP readiness 是当前 ZCode / OpenCode 会话侧状态。PubMed 不可见不是 Zotero 检索失败，而是可选 PubMed 扩展层未接入。

如果验证成功，会看到类似：

```text
✅ frontmatter parsed; version 2.1.1
✅ markdown code fences balanced
✅ required workflow headings present
✅ section numbering is consistent
✅ evidence package export requirements present
✅ RIS export requirements present
✅ appendix template definitions present
✅ Evidence Review report template sections present
✅ external-tool availability guards present

All validations passed.
```

---

## 4. 安装目标与同步方式

`scripts/install-skill.sh` 用于把仓库中的最新版 `zotero-evidence-review` 同步到不同 skill 目录，避免“仓库版本已更新，但全局安装版本仍是旧版”的漂移问题。

### 4.1 安装到不同目标

```bash
# ZCode 全局目录（推荐给 ZCode 用户）
scripts/install-skill.sh --target zcode --backup

# OpenCode 全局目录（推荐给 OpenCode 用户）
scripts/install-skill.sh --target opencode --backup

# 当前仓库项目级 OpenCode skill 目录
scripts/install-skill.sh --target project --backup

# 同时同步到 ZCode + OpenCode + 项目级目录
scripts/install-skill.sh --target all --backup
```

### 4.2 目标路径

| `--target` | 安装路径 |
|---|---|
| `zcode` | `~/.zcode/skills/zotero-evidence-review` |
| `opencode` | `~/.config/opencode/skills/zotero-evidence-review` |
| `project` | 当前仓库的 `.opencode/skills/zotero-evidence-review` |
| `all` | 同步到以上三个位置 |

### 4.3 备份规则

加上 `--backup` 后，如果目标目录已存在，脚本会先创建备份：

```text
zotero-evidence-review.backup-YYYYmmdd-HHMMSS
```

然后再覆盖安装。建议每次更新都使用 `--backup`。

---

## 5. 配置 Zotero MCP

`zotero-evidence-review` 需要通过 Zotero MCP 访问 Zotero 本地库。

### 5.1 安装 zotero-mcp

推荐使用 `pipx`：

```bash
pipx install "zotero-mcp-server[all]"
```

也可以使用 `uv`：

```bash
uv tool install "zotero-mcp-server[all]"
```

安装后检查：

```bash
which zotero-mcp
zotero-mcp version
```

如果命令找不到，请确认 `pipx` / `uv` 的 bin 目录已经加入 `PATH`。

### 5.2 Agent IDE MCP 配置总原则

`zotero-evidence-review` 只依赖“当前会话中可见的 MCP tools”，不绑定某一个客户端。OpenCode、ZCode、Claude Desktop、Cherry Studio 等 Agent IDE 都可以使用，但它们的配置文件路径和 JSON 结构并不相同，不能把某个客户端的示例原样复制到另一个客户端。

| 客户端 | 常见配置位置 | MCP 配置形态 |
|---|---|---|
| OpenCode | `~/.config/opencode/opencode.json` | 顶层 `mcp`，server 名直接放在 `mcp` 下 |
| ZCode v2 | `~/.zcode/v2/config.json` | 顶层 `mcp`，server 名直接放在 `mcp` 下 |
| ZCode CLI 旧配置/兼容层 | `~/.zcode/cli/config.json` | `mcp.servers` |
| Claude Desktop / 部分 GUI 客户端 | 客户端自己的配置文件 | 常见为 `mcpServers` |

配置完成后必须重启对应 Agent IDE 或开启新会话；只要工具列表里能看到 Zotero / PubMed 相关 MCP tools，skill 就能调用。

### 5.3 OpenCode MCP 配置示例

OpenCode 配置文件通常位于：

```text
~/.config/opencode/opencode.json
```

示例配置：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "zotero": {
      "type": "local",
      "command": ["/path/to/zotero-mcp", "serve"],
      "environment": {
        "ZOTERO_LOCAL": "true"
      },
      "enabled": true
    }
  }
}
```

把 `/path/to/zotero-mcp` 替换为：

```bash
which zotero-mcp
```

输出的真实路径。

### 5.4 ZCode MCP 配置方式

ZCode 有多个配置层。当前桌面版 / v2 主要读取：

```text
~/.zcode/v2/config.json
```

配置形态与 OpenCode 类似，使用顶层 `mcp`：

```json
{
  "mcp": {
    "zotero": {
      "type": "local",
      "command": ["/path/to/zotero-mcp", "serve"],
      "environment": {
        "ZOTERO_LOCAL": "true"
      },
      "enabled": true
    }
  }
}
```

部分 ZCode CLI / 旧配置仍可能使用：

```text
~/.zcode/cli/config.json
```

并采用 `mcp.servers` 形态：

```json
{
  "mcp": {
    "servers": {
      "zotero": {
        "type": "stdio",
        "command": "/path/to/zotero-mcp",
        "args": ["serve"],
        "environment": {
          "ZOTERO_LOCAL": "true"
        },
        "enabled": true
      }
    }
  }
}
```

如果通过 ZCode 界面添加 MCP Server，也要确认最终写入的是当前 ZCode 实际读取的配置层。修改配置后请完全重启 ZCode；仅刷新当前聊天通常不会重新加载 MCP。

更多配置细节见：[Zotero_MCP_OpenCode_Guide.md](./Zotero_MCP_OpenCode_Guide.md)。

---

## 6. 构建与更新语义索引

语义搜索依赖 zotero-mcp 的本地索引。首次使用前建议构建一次。

```bash
# 快速索引：主要处理元数据，适合首次测试
zotero-mcp update-db

# 全文索引：更适合证据核实和段落补引用，但耗时更长
zotero-mcp update-db --fulltext

# 查看索引状态
zotero-mcp db-status
```

高级排障时才建议使用强制重建：

```bash
zotero-mcp update-db --force-rebuild
```

> 注意：在 skill 工作流中，健康检查默认只读，不会自动重建索引。只有用户明确确认后，才应执行索引更新或强制重建等维护操作。

---

## 7. 使用教程与提示词示例

安装并配置完成后，在 OpenCode / ZCode 中直接对话即可。最简单的方式是用 `/zotero-evidence-review` 开头，然后用一句话说明需求；skill 会自动识别检索、段落补引用、Evidence Package 导出、引用核实或健康检查工作流。

推荐短提示词：

```text
/zotero-evidence-review 帮我给下面这段草稿找证据并补引用：……
```

```text
/zotero-evidence-review 帮我导出 Evidence Package：Markdown 报告 + EndNote RIS。
```

```text
/zotero-evidence-review 只在聊天输出，不要生成文件：帮我分析这段话的证据和推荐引用。
```

如果不用 slash command，也可以直接说“帮我补引用”“帮我导出 Evidence Package”等自然语言需求；只要意图清楚，skill 会自动路由。

### 7.0 端到端运行总览

最常用的完整路径如下：

```text
安装/同步 skill → 配置 Zotero MCP → 构建语义索引 → 在 ZCode/OpenCode 中发起请求 → intent routing → Zotero local search → paragraph/search evidence analysis → PubMed conditional expansion → metadata QC → Markdown report + EndNote RIS
```

| 需求类型 | 默认路线 | PubMed MCP 用法 | 文件输出 |
|---|---|---|---|
| 找文献 / 主题综述 | Module 1：Zotero 语义+结构检索 | 生物医学主题在 Zotero 后条件性扩展 | 默认聊天输出；用户要求时导出 |
| 段落找证据、找引文、补引用 | Module 2 → Module 2.5 完整 Paragraph Citation Package Workflow | Zotero 本地检索后自动 PubMed expansion；按 DOI/PMID 去重 | 默认生成 Markdown report + EndNote RIS |
| 精确核实某条引用是否支持某主张 | Module 3：读取元数据/全文并逐条判断 | 仅在需要 PMID 元数据、外部摘要或 OA/full-text triage 时使用 | 默认聊天输出 |
| 库状态、索引、PDF 覆盖率 | Module 0.5：只读健康检查 | 不需要 PubMed | 不导出，除非用户另行要求 |
| 只想快速看看，不要文件 | 对应模块的 chat-only 路线 | 可用则标注实际 PubMed 状态 | 不生成文件 |

语言与格式约定：

- 保存的 Markdown 结果报告默认 **中文优先**：标题、解释、综合建议、风险提示、metadata QC 说明用中文。
- 英文论文草稿的 `Recommended Manuscript Text` / 润色段落可继续保持英文；中文草稿保持中文，除非用户明确要求翻译。
- 文章标题、期刊名、作者名、DOI、PMID、Zotero key、URL、数据库名等官方元数据保持原文/官方格式，通常不翻译。
- EndNote 导入文件默认是 **RIS**，不是 EndNote XML；`.ris` 文件必须只包含标准 RIS records，不加入 Markdown 标题、中文解释、代码围栏或注释。

几个关键规则：

- 段落找证据、找引文、补引用、推荐 citation placement，或用一句话请求可复用写作输出时，默认进入完整 **Paragraph Citation Package Workflow (Module 2 + Module 2.5)** 并写出两个文件。
- `/zotero-evidence-review` 是推荐入口；后面只需用一句话说清楚“找证据、补引用、导出报告、核实引用或检查库状态”，不需要手动选择模块。
- 如果只想在聊天中查看证据矩阵、推荐引用和 diff 段落，请在请求中明确写 `不要生成文件`、`只在聊天输出`、`不导出` 或 `chat only`。
- PubMed 只在当前环境确实配置并可见 PubMed-capable MCP 工具时才会执行；不可用时报告 query 和 `⚠️ Tool unavailable; search not executed`。
- Evidence Package 由 agent 按 workflow 生成；本仓库脚本负责安装同步和静态校验，不是独立的 RIS/report 生成 CLI。

### 7.1 文献检索

```text
/zotero-evidence-review 搜 Zotero 库中关于 CRISPR base editing off-target effects 的论文，列出最相关的 10 篇。
```

```text
/zotero-evidence-review 查找 Zotero 中关于 climate change and cardiovascular health 的文献，并说明为什么相关。
```

### 7.2 Collection / Tag 范围检索

```text
只在我的 “AI in Medicine” collection 中搜索 large language models for clinical decision support 的文献，按相关性排序。
```

```text
查找带有 systematic-review 或 meta-analysis 标签、主题与 inflammation and atherosclerosis 相关的条目。
```

### 7.3 段落证据与补引用

默认行为：当你用 `/zotero-evidence-review` 或直接说“找引文、补引用、推荐引用、citation placement”时，skill 会执行一个完整的 **Paragraph Citation Package Workflow**，而不是拆成两个独立流程。只有明确写 `不要生成文件`、`只在聊天输出`、`不导出` 或 `chat only`，才会停在聊天版段落分析。

```text
paragraph → claim extraction → Zotero local search → evidence matrix + citation placement + diff paragraph → PubMed expansion → Zotero/PubMed matching + metadata QC → Markdown report + EndNote RIS
```

PubMed expansion 会在 Zotero 本地检索后自动尝试执行，但前提是当前环境确实配置并可见 PubMed-capable MCP 工具。

```text
/zotero-evidence-review 帮我给下面这段论文草稿找证据并补引用，生成 Markdown evidence report 和 EndNote RIS：

「慢性炎症通过激活 JAK-STAT 通路促进动脉粥样硬化进展，并可能增加心血管事件风险……」
```

只在聊天中输出的示例：

```text
/zotero-evidence-review 只在聊天输出，不要生成文件：帮我给下面这段论文草稿做证据链分析并补引用。

「慢性炎症通过激活 JAK-STAT 通路促进动脉粥样硬化进展，并可能增加心血管事件风险……」
```

### 7.4 Evidence Package 导出

Evidence Package 是 **Paragraph Citation Package Workflow** 的导出阶段，由 OpenCode / ZCode agent 按 `zotero-evidence-review` workflow 执行：agent 负责 Zotero 本地检索、PubMed 条件扩展、匹配质控、写入 Markdown 与 RIS；仓库脚本目前负责安装同步和静态校验，并不是独立的 RIS 生成 CLI。

完整导出流程：

```text
paragraph/search → claim extraction or search synthesis → Zotero local search → canonical Zotero metadata + PDF links → automatic PubMed expansion as a second evidence source when available → combined evidence synthesis and deduplication → reference export standardization by PMID/DOI → metadata QC → Markdown evidence report + EndNote RIS
```

运行检查点：

1. Zotero 条目进入报告或 RIS 前，必须读取 canonical metadata；不要凭记忆补齐作者、标题、期刊、年份、DOI 或 PMID。
2. Zotero 本地检索和 PubMed 扩展是两个证据来源步骤；报告中分别标记 `Zotero`、`PubMed` 或 `Zotero + PubMed`。
3. Zotero 和 PubMed 结果必须按 DOI、PMID、规范化标题和作者+年份+期刊去重，避免同一文献重复进入推荐列表。
4. RIS 导出阶段再用 PMID/DOI 重新标准化参考文献元数据：优先 PMID/PubMed，其次 DOI；无法在线核验时使用已检查的 Zotero 或 PubMed 来源元数据。
5. PubMed 状态必须写清：`Completed`、`⚠️ Tool unavailable; search not executed` 或 `Failed; query reported`。
6. RIS 必须是 plain RIS records；不要混入 Markdown 标题、解释文字、代码围栏或注释。
7. 最终聊天回复只列出生成文件路径和关键 warnings，不重复整份报告。

```text
/zotero-evidence-review 请围绕下面这段讨论生成 Evidence Package：自动检索 Zotero 证据，条件性尝试 PubMed 扩展，保存 Markdown 证据报告，并生成可导入 EndNote 的 RIS 文件。

「久坐行为可能与 PCOS 发生风险相关，但既往队列研究证据仍不一致……」
```

默认只生成两个文件，并放入能体现 skill 来源的固定输出根目录；每次运行再用 LLM 简短主题概括 + 日期时间后缀创建专门目录：

```text
zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_evidence_review.md
zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_references.ris
```

`brief_topic_slug` 由 agent 根据用户段落、claim 或检索问题自动概括，应短而具体，例如 `sedentary_behavior_pcos`，不要使用 `topic`、`references`、`output` 等泛名。`YYYY-MM-DD_HHMMSS` 使用当前本地日期时间到秒；如果同名目录已存在，使用 `_v2`、`_v3` 等目录后缀，默认不覆盖旧结果。

RIS 导出会过滤 Zotero 个人/流程标签（例如 emoji、纯符号、`/reading` 这类以 `/` 开头的标签），只保留学术关键词，以提高 EndNote 导入兼容性。

如果当前环境未配置 PubMed-capable MCP 工具，skill 只会输出可复制 PubMed query，并标注 `⚠️ Tool unavailable; search not executed`；不会声称已完成 PubMed 检索，也不会生成 PubMed-only RIS records.

### 7.5 引用核实

```text
请核实这篇文献是否真的支持以下主张：
主张：IL-6 receptor blockade reduces cardiovascular event risk in patients with chronic inflammation.
文献：给定 DOI / Zotero key / 标题
请读取元数据和全文，判断 fully supported、partially supported、contradicted 或 not addressed，并引用原文证据。
```

### 7.6 Zotero 库健康检查

```text
帮我做一次 Zotero library health check：检查语义索引、PDF 覆盖率、重复条目和缺失摘要。只读检查，不要修改任何条目。
```

### 7.7 Zotero 证据不足时的外部兜底

```text
如果 Zotero 库里证据不足，请说明缺口，并在外部工具可用时给出 Crossref / OpenAlex / PubMed 检索建议；如果工具不可用，只输出可复制的检索式，不要声称已经完成外部检索。
```

---

## 8. 推荐输出格式

Skill 内置了多个输出模板。普通对话可使用 Refs block、claim-evidence matrix 和 diff paragraph；当用户要求保存、导出 EndNote、生成 Evidence Package，或用 `/zotero-evidence-review` 进行段落找引文、补引用、推荐引用、citation placement 时，默认使用完整的 **Paragraph Citation Package Workflow (Module 2 + Module 2.5)**：Zotero 本地检索后自动尝试 PubMed expansion（工具可用时），再生成 Markdown report 和 RIS；除非用户明确要求 `不要生成文件` 或 `只在聊天输出`。

默认导出文件只有两类，并写入 `zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/` 目录：`{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_evidence_review.md` 和 `{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_references.ris`。`brief_topic_slug` 由 agent/LLM 对主题自动做简短概括。不要额外生成 JSON、BibTeX、EndNote XML、DOI 清单或日志文件，除非用户明确要求。

### 8.1 Evidence Package report

Markdown 报告是主要阅读界面，顶部必须明确 PubMed 是否实际执行，Reference Table 应显示证据来源（`Zotero`、`PubMed`、`Zotero + PubMed`），Metadata QC 应显示 RIS standardization source：

```markdown
# 证据综述：{topic}

生成日期：{YYYY-MM-DD}
来源：Zotero 本地库；PubMed: {Completed / ⚠️ Tool unavailable; search not executed / Failed; query reported / Not executed only for explicit chat-only or non-PubMed workflows}
输入：{user paragraph, claim, or search question}

## 1. 核心结论（Bottom Line）
## 2. 推荐稿件文本（Recommended Manuscript Text）
## 3. 主张—证据矩阵（Claim–Evidence Matrix）
## 4. 引文放置建议（Citation Placement）
## 5. 参考文献表（Reference Table）
## 6. Zotero 检索总结（Zotero Search Summary）
## 7. PubMed 扩展检索（PubMed Expansion）
## 8. 综合写作建议（Integrated Writing Advice）
## 9. 证据缺口与审稿风险（Gaps and Reviewer-risk Assessment）
## 10. 元数据质量控制（Metadata Quality Control）
## 11. 导出文件（Export File）
```

### 8.2 Reference Table

Zotero item key 不作为主要阅读对象展示，只隐藏在可点击链接中；DOI 和 PMID 尽量用链接呈现。

```markdown
| # | Citation | Year | Study type | Main use | Evidence source | Zotero | PDF | DOI | PMID | Collection |
|---|----------|------|------------|----------|-----------------|--------|-----|-----|------|------------|
| 1 | Author et al., *Journal* | 2024 | Systematic review | ... | Zotero + PubMed | [Item](zotero://select/items/0_KEY) | [PDF](zotero://open-pdf/library/items/ATTACHMENT_KEY) | [DOI](https://doi.org/10.xxxx/xxxx) | [PMID](https://pubmed.ncbi.nlm.nih.gov/PMID/) | Collection name |
```

### 8.3 PubMed Expansion

PubMed 是 Paragraph Citation Package Workflow 中的条件扩展步骤：段落引文导出时，skill 会在 Zotero local search 后自动尝试 PubMed expansion；只有当前环境确实配置并可见 PubMed-capable MCP 工具时，才能声称已完成 PubMed 检索。

#### PubMed 工具配置

本仓库只提供 `zotero-evidence-review` skill，不内置 PubMed MCP server。**结论是：需要你先把 PubMed MCP server 配置到你正在使用的 Agent IDE；skill 负责识别并调用当前会话中已经可见的 PubMed 工具。** README 只保留 quickstart 和协同原则；完整安装、构建、launcher、NCBI API key 与 smoke-test 细节请以 [`docs/PANCREPAL_PUBMED_MCP_GUIDE.md`](./docs/PANCREPAL_PUBMED_MCP_GUIDE.md) 为准。

不要把 OpenCode、ZCode、Claude Desktop、Cherry Studio 等客户端的 MCP 配置示例混用：它们的配置路径和 JSON 形态可能不同。常见区别如下：

| 客户端 | 常见配置位置 | MCP 配置形态 |
|---|---|---|
| OpenCode | `~/.config/opencode/opencode.json` | 顶层 `mcp`，server 名直接放在 `mcp` 下 |
| ZCode v2 | `~/.zcode/v2/config.json` | 顶层 `mcp`，server 名直接放在 `mcp` 下 |
| ZCode CLI 旧配置/兼容层 | `~/.zcode/cli/config.json` | `mcp.servers` |
| Claude Desktop / 部分 GUI 客户端 | 客户端自己的配置文件 | 常见为 `mcpServers` |

配置完成后必须完全重启对应 Agent IDE 或开启新会话；只要当前工具列表里能看到 PubMed / NCBI 相关 MCP tools，skill 就能调用。若工具不可见，Evidence Package 必须写 `PubMed: ⚠️ Tool unavailable; search not executed`，不能因为生成了 PubMed query 就声称已完成检索。

可以把两件事理解为分层：

| 层级 | 负责什么 | 是否由本 skill 内置 |
|------|----------|--------------------|
| PubMed MCP server | 连接 PubMed / NCBI、执行 search / fetch / fulltext / export 等工具调用 | 否，需要单独安装配置 |
| `zotero-evidence-review` skill | 生成 PubMed query、调用可见 PubMed 工具、合并 Zotero/PubMed 结果、去重、写 Evidence Report + RIS | 是 |

当前已知可接入方案有两类：

1. **PancrePal-xiaoyibao/mcp-pubmed-server-pancrpal**：Node.js 版，功能较完整，当前常见工具包括 `pubmed_search`、`pubmed_get_details`、`pubmed_extract_info`、`pubmed_find_related`、`pubmed_detect_fulltext`、`pubmed_download_fulltext`、`pubmed_system_status`、`pubmed_manage_cache`。适合 `zotero-evidence-review` 的默认 PubMed 扩展层。
2. **andybrandt/mcp-simple-pubmed**：Python 版，部署更轻，适合基础 PubMed 搜索与论文详情/全文获取。

二选一即可；不要在没有需要时同时启用多个 PubMed MCP，以免 agent 面对多个相似工具时路由混乱。

##### Zotero + PubMed 推荐协同方式

| 阶段 | 首选 MCP | 使用方式 |
|---|---|---|
| 本地证据检索 | Zotero MCP | 先用语义/关键词/collection/tag 检索用户本地库，保留 Zotero item、PDF、notes、annotations 与 collection 上下文。 |
| 生物医学外部扩展 | PubMed MCP | 用 `pubmed_search` 扩展 Zotero 未覆盖的医学文献，并在报告中单独标记 `PubMed` 来源。 |
| 关键文献追踪 | PubMed MCP | 对高相关 PMID 使用 `pubmed_find_related` 查 similar/reviews，避免只靠关键词遗漏综述或邻近机制。 |
| 元数据标准化 | PubMed MCP + Zotero MCP | 有 PMID 时优先 `pubmed_get_details`，没有 PMID 但有 DOI 时走 DOI 元数据；Zotero 条目仍保留本地链接。 |
| 全文/OA 检测 | PubMed MCP | 需要全文时先 `pubmed_detect_fulltext`，只有 OA 可用且有必要时再 `pubmed_download_fulltext`；下载物不自动等同 Zotero 附件。 |
| RIS/EndNote 导出 | 可见工具优先 | 如果 PubMed MCP 当前暴露 RIS/NBIB/EndNote/BibTeX exporter，则优先用它处理 PubMed-only records；否则从 `pubmed_get_details` 已检查元数据生成 RIS。 |

##### 获取并配置 NCBI API key

PubMed MCP 可以匿名访问 PubMed，但匿名模式通常约 3 次/秒；配置 NCBI API key 后通常约 10 次/秒，更适合批量检索、详情抓取和全文/OA 检测。

1. 打开 `https://account.ncbi.nlm.nih.gov/settings/`。
2. 登录或注册 NCBI 账户。
3. 找到 `API Key Management`，点击 `Create an API Key`。
4. 复制生成的 key，并准备一个真实可联系邮箱作为 `PUBMED_EMAIL`。
5. 不要把真实 key 提交到 Git 仓库；只写入本机 `.env` 或 Agent IDE 的用户级配置文件。

##### 方案 A：PancrePal PubMed MCP（Node.js）

```bash
git clone https://github.com/PancrePal-xiaoyibao/mcp-pubmed-server-pancrpal.git ~/mcp-pubmed-server-pancrpal
cd ~/mcp-pubmed-server-pancrpal
npm install
npm run build
# 可选：匿名模式可不创建 .env；需要 API key 时再 cp .env.example .env 并填写 PUBMED_API_KEY / PUBMED_EMAIL
ABSTRACT_MODE=deep FULLTEXT_MODE=enabled MCP_TRANSPORT=stdio node dist/index.js
```

上面的 `node dist/index.js` 适合在终端中做一次本地 smoke test。ZCode / OpenCode 尤其是 GUI 启动时可能不继承 shell 的 `PATH`，因此长期配置建议使用绝对路径 launcher，而不是直接写裸 `node`。

创建 launcher 示例：

```bash
mkdir -p /Users/daxuan/.local/bin
cat > /Users/daxuan/.local/bin/pubmed-mcp <<'EOF'
#!/usr/bin/env bash
export ABSTRACT_MODE="${ABSTRACT_MODE:-deep}"
export FULLTEXT_MODE="${FULLTEXT_MODE:-enabled}"
export MCP_TRANSPORT="${MCP_TRANSPORT:-stdio}"
exec /opt/homebrew/bin/node /Users/daxuan/mcp-pubmed-server-pancrpal/dist/index.js
EOF
chmod +x /Users/daxuan/.local/bin/pubmed-mcp
```

请把 `/opt/homebrew/bin/node` 与 `/Users/daxuan/mcp-pubmed-server-pancrpal/dist/index.js` 替换为本机真实路径。看到类似 `PubMed MCP Server ... running on stdio`、`abstract=deep`、`fulltext=enabled` 后，再写入当前 Agent IDE 的 MCP 配置。下面示例使用匿名模式，不要求 `PUBMED_API_KEY` / `PUBMED_EMAIL`；如需 API key，可把这两个变量加入 `environment`。

OpenCode / ZCode v2 使用顶层 `mcp`：

```json
{
  "mcp": {
    "pubmed": {
      "type": "local",
      "command": ["/Users/daxuan/.local/bin/pubmed-mcp"],
      "environment": {
        "ABSTRACT_MODE": "deep",
        "FULLTEXT_MODE": "enabled",
        "MCP_TRANSPORT": "stdio"
      },
      "enabled": true
    }
  }
}
```

ZCode CLI 旧配置/兼容层可能使用 `mcp.servers`：

```json
{
  "mcp": {
    "servers": {
      "pubmed": {
        "type": "stdio",
        "command": "/Users/daxuan/.local/bin/pubmed-mcp",
        "args": [],
        "environment": {
          "ABSTRACT_MODE": "deep",
          "FULLTEXT_MODE": "enabled",
          "MCP_TRANSPORT": "stdio"
        },
        "enabled": true
      }
    }
  }
}
```

Claude Desktop / 部分 GUI 客户端常见为 `mcpServers`，请按对应客户端文档改写，不要把 `mcpServers` 原样粘贴到 OpenCode 或 ZCode v2。

##### 方案 B：mcp-simple-pubmed（Python）

```bash
conda create -n simple-pubmed python=3.10
conda activate simple-pubmed
pip install mcp-simple-pubmed
python -m mcp_simple_pubmed
```

Agent IDE 顶层 `mcp` 配置示例：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "zotero": {
      "type": "local",
      "command": ["/Users/daxuan/.local/bin/zotero-mcp", "serve"],
      "environment": {
        "ZOTERO_LOCAL": "true"
      },
      "enabled": true
    },
    "simple-pubmed": {
      "type": "local",
      "command": ["/opt/miniconda3/envs/simple-pubmed/bin/python", "-m", "mcp_simple_pubmed"],
      "environment": {
        "PUBMED_EMAIL": "你的邮箱地址",
        "PUBMED_API_KEY": "你的NCBI API key"
      },
      "enabled": true
    }
  }
}
```

请把 Python 路径替换为你机器上真实路径，可用下面命令查看：

```bash
conda run -n simple-pubmed which python
```

##### 配置后验证

配置后重启 OpenCode / ZCode 会话，并检查 MCP 列表或当前工具清单里是否出现 PubMed/NCBI 相关工具。只有工具在当前会话可见时，报告里的 PubMed 状态才应写为 `Completed`。

```markdown
## 7. PubMed Expansion
Date: {YYYY-MM-DD}
Database: PubMed
Status: Completed / ⚠️ Tool unavailable; search not executed / Failed; query reported

Query:
~~~text
{copyable PubMed query}
~~~
```

当 PubMed 工具不可用时，只输出 query 与状态 `⚠️ Tool unavailable; search not executed`，不生成 PubMed-only RIS records。此时可复制报告中的 PubMed query 到 PubMed 网页手动检索，或先完成上述 MCP 配置后重新运行 `/zotero-evidence-review`。

### 8.4 Reviewer-risk 与 Metadata QC

Reviewer-risk 应指向具体主张或句子，方便回到原文修改；Metadata QC 应在导出信息前独立显示。

```markdown
## 9. Gaps and Reviewer-risk Assessment
| Affected claim / sentence | Risk | Severity | Evidence basis | Suggested fix |
|---------------------------|------|----------|----------------|---------------|
| ... | Overstating causal evidence | High | Observational evidence only | Replace causal wording with association wording |

## 10. Metadata Quality Control
| Citation | Missing metadata | Metadata mismatch | Duplicate warning | Evidence source | RIS standardization source | RIS action |
|----------|------------------|-------------------|-------------------|-----------------|----------------------------|------------|
| Author Year | DOI / PMID / pages / none | Possible metadata mismatch / none | Possible duplicate / none | Zotero / PubMed / Zotero + PubMed | PMID/PubMed / DOI / Zotero metadata / PubMed metadata | Include / exclude / needs manual check |
```

### 8.5 RIS export snippet

RIS 文件必须是 plain RIS records，不要混入 Markdown 标题、说明文字、代码围栏或注释。

```ris
TY  - JOUR
AU  - Last, First
PY  - 2024
TI  - Article title
JO  - Journal name
DO  - 10.xxxx/xxxx
AN  - PMID
N1  - Zotero key: XXXXXXXX
ER  -
```

EndNote 导入建议步骤：

1. 在 EndNote 中选择 `File → Import → File`。
2. 选择 Evidence Package 目录中的 `*_references.ris`。
3. `Import Option` 选择 `Reference Manager (RIS)` 或 `RIS`。
4. `Text Translation` 选择 `UTF-8`。
5. 首次测试或担心污染现有 library 时，先导入一个空白 EndNote library。
6. 导入后检查重复项；必要时用 EndNote 的 duplicate 管理功能合并。

如果 EndNote 报错，先确认 `.ris` 文件没有 Markdown 标题、中文解释、代码围栏、emoji、个人流程标签或不完整 record；每条记录都应以 `TY  -` 开始，并以 `ER  -` 结束。

### 8.6 Chat-only templates

不需要保存文件时，可继续使用简短对话模板：`REFS_BLOCK`、`CLAIM_EVIDENCE_MATRIX`、`WRITING_SUGGESTIONS_TABLE`、`DIFF_REVISED_PARAGRAPH` 和 `VERIFICATION_REPORT`。完整规范以 `zotero-evidence-review/SKILL.md` 的 Appendix 为准。

## 9. 安全与可用性规则

本 skill 的设计重点是“可追溯”和“不过度声称”。

- **不伪造引用**：不得虚构 citation、DOI、PMID、Zotero key、标题、作者、期刊或年份。
- **健康检查只读**：默认只检查状态，不重建索引、不合并重复项、不改标签、不删除条目。
- **破坏性或批量操作需确认**：删除条目、批量改标签、合并重复项、移动 collection、覆盖 notes/annotations 前必须获得明确确认。
- **外部 MCP 工具需可用才使用**：Crossref、OpenAlex、Semantic Scholar、PubMed、CNKI/CDP、WebSearch 等外部工具只有在当前环境已配置时才能声称执行；否则只能提供可复制检索式。
- **PubMed 是条件能力**：段落引文导出时，PubMed expansion 是 Zotero 本地检索后的自动尝试步骤；但当前环境未配置且可见 PubMed-capable MCP 工具时，skill 只输出可复制 PubMed query，不声称已完成 PubMed 检索，也不生成 PubMed-only RIS records。
- **不可用检查必须标注**：工具不可用、Zotero 未连接、查询不支持时，输出 `⚠️` 并解释限制，不估算、不编造数量。
- **全文证据优先**：核实具体主张时优先读取 PDF/全文；只有元数据不足以证明具体实验结论或统计结果。
- **输出与隐私卫生**：`zotero-evidence-output/` 中的 Markdown report 和 RIS 可能包含未发表稿件、Zotero 本地链接、笔记摘要、检索策略和待引用文献；除非明确打算共享，不要提交到 Git 或公开仓库。
- **密钥卫生**：不要提交 `PUBMED_API_KEY`、`PUBMED_EMAIL`、本机 MCP 私有配置、`.env` 或含真实 token 的截图。

---

## 10. 仓库结构

```text
zotero-skills/
├── README.md
├── Zotero_MCP_OpenCode_Guide.md
├── zotero-evidence-review/
│   └── SKILL.md
├── scripts/
│   ├── install-skill.sh
│   └── validate-skill.py
├── docs/
│   ├── DEVELOPMENT_PLAN.md
│   ├── DEVELOPMENT_PLAN00.md
│   └── ZOTERO_EVIDENCE_REVIEW_OUTPUT_PLAN.md
└── .opencode/                 # 安装脚本可生成；通常不需要手动维护
    └── skills/
        └── zotero-evidence-review/
```

| 路径 | 说明 |
|---|---|
| `zotero-evidence-review/SKILL.md` | 核心 skill 定义文件；当前工作流的权威规范。 |
| `scripts/install-skill.sh` | 安装/同步 skill 到 ZCode、OpenCode 或项目目录。 |
| `scripts/validate-skill.py` | 静态验证 SKILL.md 的元数据、章节、模板和安全防护说明；不执行 Zotero/PubMed 工作流。 |
| `.opencode/skills/` | 运行 `scripts/install-skill.sh --target project` 后生成的项目级 OpenCode skill 目录。 |
| `Zotero_MCP_OpenCode_Guide.md` | 更详细的 Zotero MCP 与 OpenCode 配置指南。 |
| `docs/` | 规划、设计和历史文档；当前行为以 `README.md` 与 `zotero-evidence-review/SKILL.md` 为准。 |

---

## 11. 常见问题排查

### 11.1 ZCode / OpenCode 看不到 skill

请重新同步到对应目录：

```bash
# ZCode
scripts/install-skill.sh --target zcode --backup

# OpenCode
scripts/install-skill.sh --target opencode --backup
```

然后重启或刷新 ZCode / OpenCode 会话。确认目录存在：

```text
~/.zcode/skills/zotero-evidence-review
~/.config/opencode/skills/zotero-evidence-review
```

### 11.2 Zotero MCP 报 connection refused

常见原因：Zotero 没打开，或本地访问未启用。

检查：

1. 打开 Zotero。
2. 在 Zotero 设置中启用“允许其他应用程序访问 Zotero”。
3. 确认 MCP command 指向真实的 `zotero-mcp` 路径。
4. 重启 OpenCode / ZCode 会话。

### 11.3 语义搜索没有结果

先查看索引状态。以下是用户手动运行的 CLI 排障命令；与 skill 的只读健康检查不同，agent 不会在健康检查中自动重建索引，除非你明确确认维护操作。

```bash
zotero-mcp db-status
```

如果没有索引或索引过旧：

```bash
zotero-mcp update-db
zotero-mcp update-db --fulltext
```

如果刚更换嵌入模型或索引损坏，再考虑：

```bash
zotero-mcp update-db --force-rebuild
```

### 11.4 EndNote 导入 RIS 时提示 Database error

这类错误通常首先指向 EndNote 本地 library 被占用、锁定或损坏，不一定代表 RIS 文件本身错误。建议按顺序排查：

1. 关闭所有 EndNote 窗口，确认没有其他用户或同步进程正在写入同一个 library。
2. 重启 EndNote 后重试导入。
3. 新建一个空白测试 library，再导入同一个 RIS；如果新库可导入，原 library 可能需要 EndNote 的 `Tools → Recover Library`。
4. 如果新库也失败，再检查 RIS：必须是 plain RIS records，不能有 Markdown、代码围栏、说明文字、emoji 或个人流程标签。
5. 对只有 DOI/PMID 的记录，可在 EndNote 中用 DOI/PMID 重新检索作为备用方案；但 Evidence Package 的默认交付仍是 Markdown report + RIS。

### 11.5 重复条目检查提示库太大

如果 Zotero 库很大，重复项扫描可能提示需要缩小范围。此时按 collection 检查：

```text
请只在某个 collection_key 下查找重复条目。
```

或先让助手列出 collections，再选择一个 collection 范围进行检查。

### 11.6 GitHub Desktop 要求登录 `gh-proxy.com`

这通常是 Git 全局 URL rewrite 或 remote 地址被代理改写导致的。检查：

```bash
git remote -v
git config --global --get-regexp 'url\..*insteadOf'
```

如果看到类似：

```text
https://gh-proxy.com/https://github.com/
```

可以恢复官方 GitHub 地址：

```bash
git config --global --unset url.https://gh-proxy.com/https://github.com/.insteadOf
git remote set-url origin https://github.com/DaXuanGarden/zotero-skills.git
```

然后重新打开 GitHub Desktop 或重试 push。

---

## 12. 进阶文档

- [Zotero_MCP_OpenCode_Guide.md](./Zotero_MCP_OpenCode_Guide.md)：Zotero MCP 安装、OpenCode 配置、语义索引、CLI 使用和常见问题。
- [`docs/ZOTERO_EVIDENCE_REVIEW_OUTPUT_PLAN.md`](./docs/ZOTERO_EVIDENCE_REVIEW_OUTPUT_PLAN.md)：Evidence Package 输出设计和验收标准；部分文件名示例可能是历史规划，当前默认以 README/SKILL.md 为准。
- [`docs/DEVELOPMENT_PLAN.md`](./docs/DEVELOPMENT_PLAN.md)：skill 设计与开发计划，包含已实现和历史规划内容。
- [`docs/DEVELOPMENT_PLAN00.md`](./docs/DEVELOPMENT_PLAN00.md)：早期规划记录。

> 当前权威工作流规范：`zotero-evidence-review/SKILL.md`；当前用户安装与使用说明：本 README。

---

## 13. 贡献

欢迎通过 Issue 或 PR 改进：

- 新的 Zotero MCP 工作流；
- 更严格的引用核实模板；
- 中文学术写作场景；
- OpenCode / ZCode 安装体验；
- 自动同步、验证与测试脚本。

提交前建议运行：

```bash
scripts/validate-skill.py
```

---

## 14. License

License: MIT
