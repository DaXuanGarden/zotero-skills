# 📚 Zotero Skills — OpenCode & Zcode 文献检索技能

> 让你的 AI 编程助手直接「读懂」你的 Zotero 文献库

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenCode](https://img.shields.io/badge/OpenCode-MCP-0175C2)](https://opencode.ai)
[![Zotero MCP](https://img.shields.io/badge/Zotero-MCP-CC2936)](https://github.com/54yyyu/zotero-mcp)

---

## ✨ 功能概览

| 技能 | 说明 |
|------|------|
| 🔍 **语义 + 结构化搜索** | 自然语言扩写为检索式，优先语义匹配，兜底关键词检索，返回相似度分数与 Zotero 直链 |
| 🔗 **证据链提取** | 输入一段话 → 拆解关键主张 → 逐条匹配库中支持/对比/背景文献 → 标记无证据的主张 |
| ✏️ **写作建议** | 输入草稿 → 分析引文密度、术语一致性 → 基于 Zotero 库给出补充引文、措辞修饰、替换引用等建议 |

---

## 🚀 快速开始

### 前置条件

- ✅ Zotero 7+ 运行中（开启「允许其他应用程序访问」）
- ✅ [zotero-mcp](https://github.com/54yyyu/zotero-mcp) 已安装：`pipx install "zotero-mcp-server[all]"`
- ✅ OpenCode 或 Zcode 已安装

### 安装 Skill

```bash
# 克隆本仓库
git clone https://github.com/DaXuanGarden/zotero-skills.git

# 复制到项目目录
cp -r zotero-skills/zotero-lit-search/ .opencode/skills/zotero-lit-search/
```

或复制到全局目录（所有项目可用）：

```bash
cp -r zotero-skills/zotero-lit-search/ ~/.config/opencode/skills/zotero-lit-search/
```

### 配置 Zotero MCP

在 `~/.config/opencode/opencode.json` 中添加：

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
zotero-mcp update-db           # 快速索引（元数据）
zotero-mcp update-db --fulltext  # 含全文（更准）
```

---

## 📖 使用方法

在 OpenCode/Zcode 中直接对话：

**搜索文献：**
> 搜索我 Zotero 库中关于 CRISPR 基因编辑的论文，列出前 5 篇

**语义搜索：**
> 帮我语义搜索与 "climate change cardiovascular health" 概念相似的文献

**证据链：**
> 这段草稿帮我拆解证据链：「慢性炎症通过激活 JAK-STAT 通路促进动脉粥样硬化……」

**写作润色：**
> 帮我润色这段讨论，并从 Zotero 库中补充合适的引用

---

## 🏗️ 仓库结构

```
zotero-skills/
├── zotero-lit-search/
│   ├── SKILL.md                   # 🎯 文献检索技能定义（核心文件）
│   └── Zotero_MCP_OpenCode_Guide.md
├── README.md
```

---

## 🔧 Zcode 用户

Zcode 支持一键导入 OpenCode 的 MCP 配置：

1. 打开 Zcode → **设置** → **MCP Servers**
2. 点击右上角 **Import** 按钮
3. 选择 **OpenCode** → 选中 Zotero → **Import**

Skill 文件放入项目 `.opencode/skills/` 目录后，Zcode 也会自动识别。

---

## 📦 依赖

- [54yyyu/zotero-mcp](https://github.com/54yyyu/zotero-mcp) — MCP 核心服务
- [OpenCode](https://opencode.ai) 或 [Zcode](https://zcode-ai.com) — AI 编程助手
- Python 3.10+, Zotero 7+

---

## 🤝 贡献

欢迎提交 Issue 或 PR 来改进这个技能！

---

## 📄 License

MIT
