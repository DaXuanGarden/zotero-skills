# Zotero MCP + OpenCode 完整使用指南

> 本文主要保留为 **OpenCode-oriented** 的 Zotero MCP 使用指南。若你使用 ZCode v2、ZCode CLI 旧配置、Claude Desktop、Cherry Studio 或其他 Agent IDE，请优先参考通用配置说明：[`README.md`](./README.md) 的 Agent IDE MCP 配置原则，以及 [`docs/PANCREPAL_PUBMED_MCP_GUIDE.md`](./docs/PANCREPAL_PUBMED_MCP_GUIDE.md) 的客户端配置矩阵。不同客户端的配置路径与 JSON 形态不同，不能把 OpenCode 示例原样复制到所有 Agent IDE。

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

## 6. 在 OpenCode / ZCode 中使用

### 6.1 基本用法

在 OpenCode / ZCode 终端中**直接对话式提问**即可。推荐用 `/zotero-evidence-review` 开头，然后用一句话说明需求；skill 会自动识别检索、段落补引用、Evidence Package 导出、引用核实或健康检查工作流。

#### 一句提示词示例

```
/zotero-evidence-review 搜 Zotero 库中关于 CRISPR 基因编辑的论文，列出前 5 篇。
```

```
/zotero-evidence-review 帮我给下面这段草稿找证据并补引用。
```

```
/zotero-evidence-review 帮我导出 Evidence Package：Markdown 报告 + EndNote RIS。
```

```
/zotero-evidence-review 只在聊天输出，不要生成文件：帮我分析这段话的证据和推荐引用。
```

#### 搜索文献

```
/zotero-evidence-review 搜 Zotero 库中关于 CRISPR 基因编辑的论文，列出前 5 篇
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

### 6.2 让 OpenCode / ZCode 主动使用 Zotero Evidence Review

在项目根目录的 `AGENTS.md` 中添加：

```markdown
## 文献引用

当用户需要搜索、引用或分析学术文献时，请优先调用 `/zotero-evidence-review`。
用户只需要简单说明需求；如果是段落找证据、补引用、推荐 citation placement、请求可复用写作输出或导出报告，默认执行完整 Paragraph Citation Package Workflow：先做 Zotero 本地检索，再把 PubMed 作为第二证据来源扩展检索，综合去重后在导出 RIS 时用 PMID/DOI 标准化参考文献元数据，最后在 `zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/` 下生成 Markdown evidence report + EndNote RIS。`brief_topic_slug` 由 agent/LLM 根据主题自动简短概括。
如果用户明确说“不要生成文件”“只在聊天输出”“不导出”或“chat only”，才停在聊天输出。
查询文献时请优先使用 Zotero 语义搜索，并在证据不足时清楚标注 gap。
```

### 6.3 PubMed 专用搜索工具配置

`zotero-mcp` 负责 Zotero 本地库，不等于 PubMed 搜索工具。`zotero-evidence-review` 在完整 Evidence Package 工作流中会自动尝试 PubMed expansion，但前提是当前 OpenCode / ZCode 会话里还配置并可见一个 PubMed-capable MCP server。

所以集成方式是：**先在客户端配置 PubMed MCP server，再由 skill 自动调用。** Skill 本身不能把 GitHub 上的 PubMed server “打包内置”进来，因为 MCP server 是独立进程，需要 Node.js/Python 环境、依赖、API key/email 和客户端配置共同启动。

如果报告出现：

```text
PubMed: ⚠️ Tool unavailable; search not executed
```

含义是：Zotero 检索已执行，但当前会话没有可调用的 PubMed/NCBI MCP 工具；报告中的 PubMed query 只是可复制检索式，不能当作已完成 PubMed 检索。

#### 6.3.1 匿名模式与 NCBI API key

PubMed MCP 可以匿名访问 PubMed，匿名模式通常约 3 次/秒；配置 NCBI API key 后通常约 10 次/秒，更适合批量检索、详情抓取和全文/OA 检测。建议先用匿名模式跑通 MCP，再按需要配置 API key。

匿名模式只需要在 MCP `environment` 中保留：

```text
ABSTRACT_MODE=deep
FULLTEXT_MODE=enabled
MCP_TRANSPORT=stdio
```

如需 API key：

1. 打开 `https://account.ncbi.nlm.nih.gov/settings/`。
2. 登录或注册 NCBI 账户。
3. 找到 `API Key Management`，点击 `Create an API Key`。
4. 复制生成的 key，并准备一个真实可联系邮箱作为 `PUBMED_EMAIL`。
5. 将 `PUBMED_API_KEY` 和 `PUBMED_EMAIL` 写入 PubMed MCP 项目的 `.env`，或写入当前 Agent IDE 对应 MCP server 的 `environment` 字段。
6. 不要把真实 key 提交到 Git 仓库；如果 key 泄露，在 NCBI 设置页删除或重新生成。

#### 6.3.2 推荐方案 A：PancrePal PubMed MCP（Node.js）

适合需要 PubMed 搜索、PMID 详情、定向信息抽取、related/review discovery、OA 全文检测/下载、缓存管理和条件性 EndNote/RIS 标准化的场景。当前常见工具包括 `pubmed_search`、`pubmed_get_details`、`pubmed_extract_info`、`pubmed_find_related`、`pubmed_detect_fulltext`、`pubmed_download_fulltext`、`pubmed_system_status`、`pubmed_manage_cache`。

```bash
git clone https://github.com/PancrePal-xiaoyibao/mcp-pubmed-server-pancrpal.git ~/mcp-pubmed-server-pancrpal
cd ~/mcp-pubmed-server-pancrpal
npm install
npm run build
ABSTRACT_MODE=deep FULLTEXT_MODE=enabled MCP_TRANSPORT=stdio node dist/index.js
```

上面的命令适合在终端中做一次本地 smoke test。ZCode / OpenCode GUI 可能不继承 shell `PATH`，因此长期 MCP 配置建议使用绝对路径 launcher：

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

请把 Node.js 和 `dist/index.js` 路径替换为本机真实路径。

测试成功后，把 server 加入当前 Agent IDE 的 MCP 配置。OpenCode 与 ZCode v2 常见为顶层 `mcp`：

```json
{
  "mcp": {
    "zotero": {
      "type": "local",
      "command": ["/Users/daxuan/.local/bin/zotero-mcp", "serve"],
      "environment": {
        "ZOTERO_LOCAL": "true"
      },
      "enabled": true
    },
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

如需 API key，把 `PUBMED_EMAIL` 和 `PUBMED_API_KEY` 加入 `pubmed.environment`。如果当前 PubMed MCP 版本直接暴露 RIS/NBIB/EndNote/BibTeX exporter，skill 会优先使用；否则使用 `pubmed_get_details` 检查后的 PMID 元数据生成 EndNote-compatible RIS。

#### 6.3.3 轻量方案 B：mcp-simple-pubmed（Python）

适合基础搜索、论文详情和全文获取。

```bash
conda create -n simple-pubmed python=3.10
conda activate simple-pubmed
pip install mcp-simple-pubmed
python -m mcp_simple_pubmed
```

查看 Python 真实路径：

```bash
conda run -n simple-pubmed which python
```

配置示例：

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

#### 6.3.4 配置注意事项

1. 不同 Agent IDE 的 MCP 配置形态不同：OpenCode 与 ZCode v2 常见为顶层 `mcp`；ZCode CLI 旧配置/兼容层可能是 `mcp.servers`；Claude、Cursor、Cherry Studio 等 GUI 客户端常见为 `mcpServers`，不能原样粘贴到 OpenCode 或 ZCode v2。
2. `command` 和路径必须换成本机真实路径。
3. PubMed 标准限速约 3 次/秒；配置 NCBI API key 后通常可到 10 次/秒。
4. 建议二选一启用 PubMed MCP，避免多个相似工具让 agent 路由混乱。
5. 保存配置后完全重启当前 Agent IDE 或开启新会话；ZCode v2 通常读取 `~/.zcode/v2/config.json`，OpenCode 通常读取 `~/.config/opencode/opencode.json`。
6. OpenCode 可用 `opencode mcp list` 验证；ZCode v2 以重启后的当前会话工具清单为准，确认同时有 `zotero` 和 `pubmed` / `ncbi` 相关工具。

使用时仍然只需调用同一个 skill：

```text
/zotero-evidence-review 帮我给下面这段草稿找证据并补引用，生成 Markdown evidence report 和 EndNote RIS。
```

若 PubMed 工具可见且检索成功，报告状态为 `Completed`，并可加入经 PubMed 元数据核验的 PubMed-only 记录；若不可见，报告会保留 `⚠️ Tool unavailable; search not executed`，并且不会生成 PubMed-only RIS records。

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

### 8.4 在 OpenCode / ZCode 中一键完成工作流示例

示例提示词：

> *"/zotero-evidence-review 帮我给下面这段草稿找证据并补引用，生成 Markdown evidence report 和 EndNote RIS：久坐行为可能与 PCOS 发生风险相关，但既往队列研究证据仍不一致……"*

默认文件会写入类似下面的主题目录，避免散落在项目根目录：

```text
zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_evidence_review.md
zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_references.ris
```

如果只想看聊天结果，不生成文件：

> *"/zotero-evidence-review 只在聊天输出，不要生成文件：帮我分析这段草稿的证据和推荐引用。"*

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

### Q: EndNote 导入 RIS 时提示 Database error？

优先检查 EndNote library 是否被占用、锁定或损坏：关闭 EndNote 并重启，或新建空白 library 测试导入同一个 RIS。若新库可导入，原 library 可能需要 EndNote 的 `Tools → Recover Library`。若新库也失败，再检查 RIS 是否混入 Markdown、说明文字、代码围栏、emoji 或个人流程标签。

### Q: 数据库损坏或模型切换后出错？

优先使用 zotero-mcp 自带的强制重建命令：

```bash
zotero-mcp update-db --force-rebuild
```

如果仍然有问题，先确认实际缓存路径、备份必要文件，并阅读 zotero-mcp 当前版本文档后再手动清理缓存。不要让 agent 在未确认路径和备份的情况下自动执行 `rm -rf`。
