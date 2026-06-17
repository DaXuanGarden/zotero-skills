# 📚 Zotero Skills — OpenCode & ZCode 文献证据审查技能

> 让 AI 助手直接检索、分析并核实你的 Zotero 文献库。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenCode](https://img.shields.io/badge/OpenCode-MCP-0175C2)](https://opencode.ai)
[![Zotero MCP](https://img.shields.io/badge/Zotero-MCP-CC2936)](https://github.com/54yyyu/zotero-mcp)

---

## ✨ 功能概览

| 能力 | 说明 |
|------|------|
| 🔍 **语义 + 结构化搜索** | 自然语言扩写为检索式，优先语义匹配，必要时兜底关键词、标签、分类检索。 |
| 🧾 **段落证据与引文分析** | 输入草稿段落 → 拆解主张 → 一次性检索证据池 → 输出主张-证据矩阵、逐句引文建议和 diff 版段落。 |
| ✅ **严格引用核实** | 针对具体主张/数据/引文读取 Zotero 元数据与全文，判断 fully supported / partially supported / contradicted / not addressed。 |
| 🩺 **库健康度检查** | 只读检查语义索引、PDF 覆盖、重复条目、缺失摘要，并明确标记不可用或未配置的检查。 |
| 🔄 **安装/同步脚本** | 使用脚本把仓库内新版 skill 同步到 ZCode、OpenCode 或项目目录，支持覆盖前备份。 |

---

## 🚀 快速开始

### 前置条件

- ✅ Zotero 7+ 运行中，并在 Zotero 设置中开启「允许其他应用程序访问」。
- ✅ [zotero-mcp](https://github.com/54yyyu/zotero-mcp) 已安装，例如：`pipx install "zotero-mcp-server[all]"`。
- ✅ OpenCode 或 ZCode 已安装。

### 安装或更新 Skill

```bash
# 克隆仓库
git clone https://github.com/DaXuanGarden/zotero-skills.git
cd zotero-skills

# 安装/更新到 ZCode 全局 skill 目录（推荐）
scripts/install-skill.sh --target zcode --backup
```

可选目标：

```bash
# 安装到 OpenCode 全局目录
scripts/install-skill.sh --target opencode --backup

# 安装到当前仓库的项目级 .opencode/skills 目录
scripts/install-skill.sh --target project --backup

# 同步到 ZCode + OpenCode + 项目目录
scripts/install-skill.sh --target all --backup
```

`--backup` 会在覆盖旧版本前创建形如 `zotero-evidence-review.backup-YYYYmmdd-HHMMSS` 的备份目录，避免仓库版本和全局安装版本漂移。

### 验证 Skill 文件

```bash
scripts/validate-skill.py
```

该脚本会检查：YAML frontmatter、Markdown code fence、关键工作流标题、章节编号、Appendix 模板、外部 MCP 可用性防护说明。

### 配置 Zotero MCP

在 OpenCode 或 ZCode 对应 MCP 配置中添加 Zotero MCP。OpenCode 示例：

```json
{
  "mcp": {
    "zotero": {
      "type": "local",
      "command": ["/path/to/zotero-mcp", "serve"],
      "environment": { "ZOTERO_LOCAL": "true" },
      "enabled": true
    }
  }
}
```

`/path/to/zotero-mcp` 替换为实际路径，可用 `which zotero-mcp` 查看。

### 构建语义索引

```bash
zotero-mcp update-db             # 快速索引（元数据）
zotero-mcp update-db --fulltext  # 含全文索引（更适合证据核实）
zotero-mcp db-status             # 查看索引状态
```

---

## 📖 使用方法

在 OpenCode/ZCode 中直接对话：

**搜索文献：**
> 搜索我 Zotero 库中关于 CRISPR 基因编辑的论文，列出前 5 篇。

**语义搜索：**
> 帮我语义搜索与 "climate change cardiovascular health" 概念相似的文献。

**段落证据与引文分析：**
> 这段草稿帮我拆解证据链并补引用：「慢性炎症通过激活 JAK-STAT 通路促进动脉粥样硬化……」

**引用核实：**
> 请验证某篇文献是否真的支持“IL-6 受体阻断剂可降低心血管事件风险”这句话。

**健康检查：**
> 帮我检查 Zotero 库状态、语义索引和 PDF 覆盖率。

---

## 🏗️ 仓库结构

```text
zotero-skills/
├── zotero-evidence-review/
│   └── SKILL.md                   # 🎯 文献证据审查 skill 定义
├── scripts/
│   ├── install-skill.sh            # 安装/同步到 ZCode、OpenCode 或项目目录
│   └── validate-skill.py           # Skill Markdown/YAML/模板验证
├── docs/                           # 规划与设计文档（如有）
├── Zotero_MCP_OpenCode_Guide.md     # Zotero MCP 配置与使用指南
└── README.md
```

---

## 🔧 ZCode 用户

ZCode 可通过 MCP Servers 设置导入或配置 Zotero MCP：

1. 打开 ZCode → **设置** → **MCP Servers**。
2. 点击右上角 **Import** 或手动添加 Zotero MCP。
3. 确认 Zotero 正在运行，并且 Zotero MCP 工具可用。
4. 使用 `scripts/install-skill.sh --target zcode --backup` 同步最新版 skill。

---

## 🛡️ 安全与可用性约定

- 健康检查默认只读，不会自动重建索引、合并重复项、改标签或删除条目。
- 外部检索工具只有在当前环境已配置时才会使用；未配置时只输出可复制的检索式。
- 不伪造 citation、DOI、PMID、Zotero key、标题、作者或期刊信息。
- 添加文献、批量改动、合并重复项、删除条目前必须获得明确确认。

---

## 📦 依赖

- [54yyyu/zotero-mcp](https://github.com/54yyyu/zotero-mcp) — Zotero MCP 服务。
- [OpenCode](https://opencode.ai) 或 [ZCode](https://zcode-ai.com) — AI 编程助手。
- Python 3.10+、Zotero 7+。

---

## 🤝 贡献

欢迎提交 Issue 或 PR 来改进这个技能。

---

## 📄 License

MIT
