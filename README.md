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
| 当前版本 | `2.1.0` |
| 兼容性 | OpenCode / ZCode |
| 主要依赖 | Zotero 7+、zotero-mcp、Python 3.10+ |
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

### 3.2 克隆仓库并安装到 ZCode（推荐）

```bash
git clone https://github.com/DaXuanGarden/zotero-skills.git
cd zotero-skills

# 安装/更新到 ZCode 全局 skill 目录，并在覆盖前备份旧版本
scripts/install-skill.sh --target zcode --backup

# 验证 skill 文件结构
scripts/validate-skill.py
```

`scripts/validate-skill.py` 是静态校验工具：它检查 `zotero-evidence-review/SKILL.md` 的 frontmatter、章节、输出模板、Evidence Package/RIS 约束和外部工具安全防护说明；它不会连接 Zotero、不会执行 PubMed 检索，也不会验证 README 的自然语言描述。

如果验证成功，会看到类似：

```text
✅ frontmatter parsed; version 2.1.0
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

### 5.2 OpenCode MCP 配置示例

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

### 5.3 ZCode MCP 配置方式

ZCode 中可通过界面添加 MCP Server：

1. 打开 ZCode。
2. 进入 **Settings / 设置** → **MCP Servers**。
3. 使用 **Import** 或手动添加 Zotero MCP。
4. Command 设置为 `zotero-mcp serve` 或实际二进制路径加 `serve`。
5. 环境变量设置：`ZOTERO_LOCAL=true`。
6. 确认 Zotero 已打开，然后重启/刷新 ZCode 会话。

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

安装并配置完成后，在 OpenCode / ZCode 中直接对话即可。建议明确说明你想要的输出格式、检索范围和证据标准。

### 7.0 端到端运行总览

最常用的完整路径如下：

```text
安装/同步 skill → 配置 Zotero MCP → 构建语义索引 → 在 ZCode/OpenCode 中发起请求 → intent routing → Zotero local search → paragraph/search evidence analysis → PubMed conditional expansion → metadata QC → Markdown report + EndNote RIS
```

几个关键规则：

- 段落找引文、补引用、推荐 citation placement 时，默认进入完整 **Paragraph Citation Package Workflow (Module 2 + Module 2.5)** 并写出两个文件。
- 如果只想在聊天中查看证据矩阵、推荐引用和 diff 段落，请在请求中明确写 `不要生成文件`、`只在聊天输出`、`不导出` 或 `chat only`。
- PubMed 只在当前环境确实配置并可见 PubMed-capable MCP 工具时才会执行；不可用时报告 query 和 `⚠️ Tool unavailable; search not executed`。
- Evidence Package 由 agent 按 workflow 生成；本仓库脚本负责安装同步和静态校验，不是独立的 RIS/report 生成 CLI。

### 7.1 文献检索

```text
搜索我 Zotero 库中关于 CRISPR base editing off-target effects 的论文，列出最相关的 10 篇，包含标题、作者、年份、期刊、DOI 和 Zotero key。
```

```text
帮我查找 Zotero 中关于 climate change and cardiovascular health 的文献，优先语义搜索，再用关键词兜底，并说明每篇为什么相关。
```

### 7.2 Collection / Tag 范围检索

```text
只在我的 “AI in Medicine” collection 中搜索 large language models for clinical decision support 的文献，按相关性排序。
```

```text
查找带有 systematic-review 或 meta-analysis 标签、主题与 inflammation and atherosclerosis 相关的条目。
```

### 7.3 段落证据与补引用

默认行为：当你说“使用技能”来做段落找引文、补引用、推荐引用或 citation placement 时，skill 会执行一个完整的 **Paragraph Citation Package Workflow**，而不是拆成两个独立流程。只有明确写 `不要生成文件`、`只在聊天输出`、`不导出` 或 `chat only`，才会停在聊天版段落分析。

```text
paragraph → claim extraction → Zotero local search → evidence matrix + citation placement + diff paragraph → PubMed expansion → Zotero/PubMed matching + metadata QC → Markdown report + EndNote RIS
```

PubMed expansion 会在 Zotero 本地检索后自动尝试执行，但前提是当前环境确实配置并可见 PubMed-capable MCP 工具。

```text
使用技能，请对下面这段论文草稿做证据链分析并补引用：
1. 拆解每个核心主张；
2. 在 Zotero 中检索支持证据；
3. 输出主张-证据矩阵；
4. 给出推荐引用；
5. 生成 Markdown evidence report 和 EndNote RIS。

「慢性炎症通过激活 JAK-STAT 通路促进动脉粥样硬化进展，并可能增加心血管事件风险……」
```

只在聊天中输出的示例：

```text
请对下面这段论文草稿做证据链分析并补引用，但不要生成文件，只在聊天输出。

「慢性炎症通过激活 JAK-STAT 通路促进动脉粥样硬化进展，并可能增加心血管事件风险……」
```

### 7.4 Evidence Package 导出

Evidence Package 是 **Paragraph Citation Package Workflow** 的导出阶段，由 OpenCode / ZCode agent 按 `zotero-evidence-review` workflow 执行：agent 负责 Zotero 本地检索、PubMed 条件扩展、匹配质控、写入 Markdown 与 RIS；仓库脚本目前负责安装同步和静态校验，并不是独立的 RIS 生成 CLI。

完整导出流程：

```text
paragraph/search → claim extraction or search synthesis → Zotero local search → canonical Zotero metadata + PDF links → automatic PubMed expansion when available → Zotero/PubMed matching → metadata QC → Markdown evidence report + EndNote RIS
```

运行检查点：

1. Zotero 条目进入报告或 RIS 前，必须读取 canonical metadata；不要凭记忆补齐作者、标题、期刊、年份、DOI 或 PMID。
2. PubMed 状态必须写清：`Completed`、`⚠️ Tool unavailable; search not executed` 或 `Failed; query reported`。
3. RIS 必须是 plain RIS records；不要混入 Markdown 标题、解释文字、代码围栏或注释。
4. 最终聊天回复只列出生成文件路径和关键 warnings，不重复整份报告。

```text
请围绕下面这段讨论生成 Evidence Package：
1. 自动检索 Zotero 证据；
2. 如果当前环境配置了 PubMed-capable MCP 工具，请进行 PubMed 扩展检索；如果不可用，只输出可复制 PubMed query，并标注 `⚠️ Tool unavailable; search not executed`；
3. 保存 Markdown 证据报告；
4. 生成可导入 EndNote 的 RIS 文件。

「久坐行为可能与 PCOS 发生风险相关，但既往队列研究证据仍不一致……」
```

默认只生成两个文件：

```text
YYYY-MM-DD_{topic_slug}_evidence_review.md
YYYY-MM-DD_{topic_slug}_references.ris
```

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

Skill 内置了多个输出模板。普通对话可使用 Refs block、claim-evidence matrix 和 diff paragraph；当用户要求保存、导出 EndNote 或生成 Evidence Package 时，推荐使用两文件输出。对于“使用技能”进行段落找引文、补引用、推荐引用或 citation placement 的请求，默认使用完整的 **Paragraph Citation Package Workflow (Module 2 + Module 2.5)**：Zotero 本地检索后自动尝试 PubMed expansion（工具可用时），再生成 Markdown report 和 RIS；除非用户明确要求 `不要生成文件` 或 `只在聊天输出`。

默认导出文件只有两类：`YYYY-MM-DD_{topic_slug}_evidence_review.md` 和 `YYYY-MM-DD_{topic_slug}_references.ris`。不要额外生成 JSON、BibTeX、EndNote XML 或日志文件，除非用户明确要求。

### 8.1 Evidence Package report

Markdown 报告是主要阅读界面，顶部必须明确 PubMed 是否实际执行：

```markdown
# Evidence Review: {topic}

Generated: {YYYY-MM-DD}
Source: Zotero local library; PubMed: {Completed / ⚠️ Tool unavailable; search not executed / Failed; query reported / Not executed only for explicit chat-only or non-PubMed workflows}
Input: {user paragraph, claim, or search question}

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

### 8.2 Reference Table

Zotero item key 不作为主要阅读对象展示，只隐藏在可点击链接中；DOI 和 PMID 尽量用链接呈现。

```markdown
| # | Citation | Year | Study type | Main use | Zotero | PDF | DOI | PMID | Collection |
|---|----------|------|------------|----------|--------|-----|-----|------|------------|
| 1 | Author et al., *Journal* | 2024 | Systematic review | ... | [Item](zotero://select/items/0_KEY) | [PDF](zotero://open-pdf/library/items/ATTACHMENT_KEY) | [DOI](https://doi.org/10.xxxx/xxxx) | [PMID](https://pubmed.ncbi.nlm.nih.gov/PMID/) | Collection name |
```

### 8.3 PubMed Expansion

PubMed 是 Paragraph Citation Package Workflow 中的条件扩展步骤：段落引文导出时，skill 会在 Zotero local search 后自动尝试 PubMed expansion；只有当前环境确实配置并可见 PubMed-capable MCP 工具时，才能声称已完成 PubMed 检索。

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

当 PubMed 工具不可用时，只输出 query 与状态 `⚠️ Tool unavailable; search not executed`，不生成 PubMed-only RIS records。

### 8.4 Reviewer-risk 与 Metadata QC

Reviewer-risk 应指向具体主张或句子，方便回到原文修改；Metadata QC 应在导出信息前独立显示。

```markdown
## 9. Gaps and Reviewer-risk Assessment
| Affected claim / sentence | Risk | Severity | Evidence basis | Suggested fix |
|---------------------------|------|----------|----------------|---------------|
| ... | Overstating causal evidence | High | Observational evidence only | Replace causal wording with association wording |

## 10. Metadata Quality Control
| Citation | Missing metadata | Metadata mismatch | Duplicate warning | RIS action |
|----------|------------------|-------------------|-------------------|------------|
| Author Year | DOI / PMID / pages / none | Possible metadata mismatch / none | Possible duplicate / none | Include / exclude / needs manual check |
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

### 11.4 重复条目检查提示库太大

如果 Zotero 库很大，重复项扫描可能提示需要缩小范围。此时按 collection 检查：

```text
请只在某个 collection_key 下查找重复条目。
```

或先让助手列出 collections，再选择一个 collection 范围进行检查。

### 11.5 GitHub Desktop 要求登录 `gh-proxy.com`

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
