# Zotero MCP + OpenCode 完整使用指南

## 目录

- [1. 概述](#1-概述)
- [2. 安装与配置](#2-安装与配置)
- [3. OpenCode MCP 配置](#3-opencode-mcp-配置)
- [4. 语义搜索配置](#4-语义搜索配置)
- [5. 数据库管理与更新](#5-数据库管理与更新)
- [6. 在 OpenCode 中使用](#6-在-opencode-中使用)
- [7. Zotero CLI 使用](#7-zotero-cli-使用)
- [8. 高级技巧](#8-高级技巧)
- [9. 常见问题](#9-常见问题)

---

## 1. 概述

**Zotero MCP**（[54yyyu/zotero-mcp](https://github.com/54yyyu/zotero-mcp)）通过 Model Context Protocol (MCP) 将 Zotero 文献库与 AI 助手（OpenCode）连接，支持：

- 多维度文献搜索（关键词、语义、标签、全文）
- 元数据查看与 BibTeX 导出
- PDF 全文提取与标注分析
- 语义搜索（AI 概念匹配，非关键词匹配）
- 文献增删改操作
- OpenCode 中直接对话式检索

---

## 2. 安装与配置

### 2.1 前置条件

- Zotero 7+ **正在运行**
- Zotero 中启用本地 API：**编辑 → 设置 → 高级 → 允许其他应用程序访问 Zotero**
- Python 3.10+
- pipx 或 uv

### 2.2 安装 zotero-mcp

```bash
# 通过 pipx 安装（推荐）
pipx install "zotero-mcp-server[all]"

# 或通过 uv
uv tool install "zotero-mcp-server[all]"
```

`[all]` 包含三个可选扩展包：

| 扩展 | 功能 |
|------|------|
| `semantic` | AI 语义搜索（基于 ChromaDB + 向量嵌入） |
| `pdf` | PDF 目录提取、EPUB 标注支持 |
| `scite` | 引用智能分析、撤稿提醒 |

安装后验证：

```bash
zotero-mcp version
zotero-mcp setup-info
```

### 2.3 升级扩展包

```bash
pipx install "zotero-mcp-server[all]" --force
```

---

## 3. OpenCode MCP 配置

### 3.1 配置文件路径

`~/.config/opencode/opencode.json`

### 3.2 配置内容

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

`/path/to/zotero-mcp` 替换为 `which zotero-mcp` 的输出。

### 3.3 验证连接

```bash
# 在项目目录中运行
opencode mcp list
```

预期输出：

```
┌  MCP Servers
│
●  ✓ zotero connected
│      /path/to/zotero-mcp serve
│
└  1 server(s)
```

---

## 4. 语义搜索配置

### 4.1 运行配置向导

```bash
zotero-mcp setup --semantic-config-only
```

按提示选择：
- **嵌入模型**：选 `1`（Default: all-MiniLM-L6-v2）—— 免费、本地运行
- **更新频率**：选 `1`（Manual）或 `3`（Daily）
- **PDF 最大页数**：默认 `10`（直接回车）
- **Zotero 数据库路径**：默认 `auto-detect`（直接回车）

### 4.2 支持的嵌入模型

| 模型 | 费用 | 是否联网 | 质量 |
|------|------|----------|------|
| all-MiniLM-L6-v2（默认） | 免费 | 本地运行 | 良好 |
| OpenAI text-embedding-3-small | 需 API 费用 | 需联网 | 优秀 |
| Gemini embedding-001 | 需 API 费用 | 需联网 | 优秀 |

### 4.3 切换模型

```bash
# 切换为 OpenAI（需设置 OPENAI_API_KEY）
zotero-mcp setup --semantic-config-only
# 然后选择 2

# 或直接修改配置文件
# ~/.config/zotero-mcp/config.json
```

### 4.4 构建语义索引

```bash
# 快速索引（仅元数据，推荐首次使用）
zotero-mcp update-db

# 完整索引（含全文，更准但慢）
zotero-mcp update-db --fulltext

# 强制重建
zotero-mcp update-db --force-rebuild

# 限数量测试
zotero-mcp update-db --limit 100

# 查看状态
zotero-mcp db-status
```

---

## 5. 数据库管理与更新

### 5.1 添加新文献后更新

当在 Zotero 中添加新文献后，需要更新语义索引才能检索到：

```bash
# 增量更新（只处理新增条目，不重建全部）
zotero-mcp update-db

# 如首次构建时未含全文，可追加
zotero-mcp update-db --fulltext
```

### 5.2 定时自动更新

```bash
# 编辑 crontab
crontab -e

# 每天凌晨 2 点自动更新
0 2 * * * /path/to/zotero-mcp update-db >> /tmp/zotero-update.log 2>&1

# 或每周更新
0 2 * * 1 /path/to/zotero-mcp update-db >> /tmp/zotero-update.log 2>&1
```

### 5.3 更换嵌入模型后重建

```bash
zotero-mcp update-db --force-rebuild
```

---

## 6. 在 OpenCode 中使用

### 6.1 基本用法

在 OpenCode 终端中**直接对话式提问**即可：

#### 搜索文献

```
搜索我 Zotero 库中关于 CRISPR 基因编辑的论文，列出前 5 篇
```

```
在 Zotero 中查找 climate change 相关的文献，给出标题、作者和年份
```

```
搜索 DOI 为 10.1038/s41586-021-03819-2 的文献详细信息
```

#### 语义搜索（概念匹配，非关键词）

```
帮我做语义搜索，找与 "mitochondrial dysfunction neurodegeneration" 概念相似的文献
```

```
找关于肿瘤免疫微环境与 CAR-T 治疗的研究，用语义搜索
```

#### 获取文献详情

```
查看这篇论文的完整元数据，包括摘要、期刊、DOI
```

```
导出这篇文献的 BibTeX 引用格式
```

#### 文献定位

```
打开 Zotero 中这篇论文的条目
```
（这会通过 `zotero://select/items/0_{ItemKey}` 协议跳转到 Zotero）

#### 分类与组织结构

```
列出我在 Zotero 中的所有顶层分类
```

```
搜索名为 "CRISPR" 的分类，列出里面的子分类
```

```
这篇论文在 Zotero 中属于哪些分类？
```

### 6.2 让 OpenCode 主动使用 Zotero

在项目根目录的 `AGENTS.md` 中添加：

```markdown
## 文献引用

当你需要搜索、引用或分析学术文献时，请使用 Zotero MCP 工具。
查询文献时请优先使用语义搜索（semantic_search）以获得更准确的概念匹配结果。
```

---

## 7. Zotero CLI 使用

不需要 AI 时，可直接在终端操作 Zotero 库：

### 搜索

```bash
# 关键词搜索
zotero-cli search "climate change"

# 语义搜索
zotero-cli search --mode semantic "tumor microenvironment immunotherapy"

# 按标签搜索
zotero-cli search --mode tag "important,reviewed"

# 限制数量
zotero-cli s "machine learning" --limit 5   # s 是 search 别名
```

### 查看文献详情

```bash
# Markdown 格式（默认）
zotero-cli get metadata ITEM_KEY

# BibTeX 格式
zotero-cli g metadata ITEM_KEY --format bibtex

# JSON 格式
zotero-cli g metadata ITEM_KEY --format json

# 获取全文
zotero-cli get fulltext ITEM_KEY
```

`ITEM_KEY` 替换为实际的 Zotero 条目 Key。

### 分类管理

```bash
# 搜索分类
zotero-cli coll search "machine learning"

# 列出所有分类
zotero-cli coll search ""
```

### 标注与笔记

```bash
# 列出标注
zotero-cli ann list ITEM_KEY

# 搜索标注
zotero-cli ann search "highlight text"
```

### 语义数据库管理

```bash
# 更新索引
zotero-cli db update

# 带全文更新
zotero-cli db update --fulltext

# 查看状态
zotero-cli db status
```

### 添加文献

```bash
# 通过 DOI 添加
zotero-cli add doi 10.1038/s41586-021-03819-2

# 通过 URL 添加
zotero-cli add url https://arxiv.org/abs/2301.00001

# 从本地文件导入
zotero-cli add file /path/to/paper.pdf
```

---

## 8. 高级技巧

### 8.1 直接打开 Zotero 条目

语义搜索结果中会显示 `Item Key`，利用 `zotero://` 协议可直接跳转：

```bash
# 格式：zotero://select/items/0_{ItemKey}
open "zotero://select/items/0_ABCD1234"
```

### 8.2 查找重复文献

```bash
zotero-cli duplicates find
```

### 8.3 获取文献的全部分类路径

在 OpenCode 中提问：

> *"这篇文章属于哪些分类？给出完整的分类路径"*

### 8.4 在 OpenCode 中一键完成工作流示例

示例提示词：

> *"在 Zotero 中用语义搜索找到与 'climate change cardiovascular disease' 最相关的 5 篇论文，列出每篇的标题、作者、期刊、年份和相似度分数，然后生成 APA 引用。"*

---

## 9. 常见问题

### Q: OpenCode 显示 zotero connected 但对话中搜不到结果？

确保：
1. Zotero 桌面端正在运行
2. Zotero 设置中已开启"允许其他应用程序访问"
3. 已在对话中明确告诉 OpenCode 使用 Zotero 工具

### Q: 新增文献后语义搜索找不到？

运行 `zotero-mcp update-db` 更新索引。默认是手动更新模式。

### Q: 语义搜索模型需要付费吗？

不需要。默认的 `all-MiniLM-L6-v2` 完全免费、本地运行、无需联网。

### Q: 如何查看文献在 Zotero 中的分类归属？

在 OpenCode 中提问，或在 Zotero 应用界面中查看条目所属分类。

### Q: 如何更新 zotero-mcp 版本？

```bash
zotero-mcp update          # 自动更新（推荐）
# 或
pipx install "zotero-mcp-server[all]" --force
```

### Q: 数据库损坏或模型切换后出错？

```bash
zotero-mcp update-db --force-rebuild
# 如果仍然有问题
rm -rf ~/.config/zotero-mcp/chroma_db
zotero-mcp update-db
```
