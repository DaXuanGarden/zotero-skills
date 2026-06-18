# PancrePal PubMed MCP 安装配置与使用教程

本文档说明如何在 Agent IDE 中接入功能较完整的 PubMed MCP server：[`PancrePal-xiaoyibao/mcp-pubmed-server-pancrpal`](https://github.com/PancrePal-xiaoyibao/mcp-pubmed-server-pancrpal)，并配合本仓库的 `zotero-evidence-review` skill 使用。

> 结论：PubMed MCP server 需要先作为独立 MCP 服务安装并配置到你正在使用的 Agent IDE；`zotero-evidence-review` skill 会在当前会话中识别可见的 PubMed 工具，并在 Evidence Package 工作流中自动调用。

---

## 1. 能力边界

### 1.1 这个 PubMed MCP 负责什么

PancrePal PubMed MCP server 负责连接 PubMed / NCBI 数据源，并提供文献搜索、PMID 详情、定向信息抽取、related/review discovery、OA 全文检测/下载和缓存管理等工具能力。实际可用工具名称以该项目当前版本暴露的 MCP tools 为准。

当前常见能力包括：

| 能力 | 常见工具 | 在 `zotero-evidence-review` 中的用途 |
|---|---|---|
| PubMed 文献搜索 | `pubmed_search` | Zotero 本地检索之后的第二层 biomedical expansion；可用 `format="compact"` 扫描、`format="detailed"` 检查候选证据。 |
| PMID 详情与规范元数据 | `pubmed_get_details` | 进入报告、去重或 RIS 的 PMID 必须先检查详情元数据。 |
| 定向字段抽取 | `pubmed_extract_info` | 需要 basic_info、authors、abstract_summary、keywords、doi_link 等字段时减少不必要的完整记录读取。 |
| related/review discovery | `pubmed_find_related` | 围绕关键 PMID 查 similar articles 或 reviews，补足综述、机制链条和邻近证据。 |
| OA/full-text 检测与下载 | `pubmed_detect_fulltext` / `pubmed_download_fulltext` | 先检测 OA/full-text 可用性；只有可用、必要且启用时下载。下载物是外部缓存，不自动等同 Zotero 附件。 |
| 缓存与系统状态 | `pubmed_manage_cache` / `pubmed_system_status` | 排错、查看匿名/API key 状态、abstract/fulltext 模式与缓存状态；清理缓存前应确认。 |
| EndNote/RIS/NBIB/BibTeX 导出 | 仅当当前 MCP 版本实际暴露 exporter | 如果没有直接 exporter，则由 skill 基于已检查的 `pubmed_get_details` 元数据生成 EndNote-compatible RIS。 |

### 1.2 `zotero-evidence-review` skill 负责什么

本仓库的 skill 不内置 PubMed server，而是在当前会话工具可见时调用它：

- 从用户段落或问题生成 PubMed query
- 先检索 Zotero 本地库
- 再把 PubMed 作为第二证据来源扩展检索
- 合并 Zotero / PubMed 结果
- 按 DOI、PMID、标题、作者年份去重
- 生成 Markdown evidence report
- 生成 EndNote-compatible RIS

如果 PubMed MCP 没有配置成功，报告会显示：

```text
PubMed: ⚠️ Tool unavailable; search not executed
```

这不是 Zotero 检索失败，而是当前会话没有可调用的 PubMed 工具。

---

## 2. 前置条件

### 2.1 系统要求

- macOS / Linux / Windows 均可，本文以 macOS 路径为主。
- Node.js `18.0.0+`
- npm
- Git
- OpenCode / ZCode / Claude Desktop / 其他支持 MCP 的 Agent IDE
- Zotero MCP 已配置好，推荐同时保留 Zotero 本地检索能力

### 2.2 检查 Node.js

```bash
node -v
npm -v
```

期望：

```text
v18.x.x 或更高
```

如果没有 Node.js，建议从以下地址安装 LTS 版本：

```text
https://nodejs.org/
```

### 2.3 匿名模式与 NCBI API key

PubMed 可以不带 API key 低频访问，当前推荐先用匿名模式跑通 MCP，再按需要配置 API key：

- 匿名模式：通常约 3 次/秒，适合日常少量检索与测试。
- 有 API key：通常约 10 次/秒，适合批量详情获取、频繁检索或全文/OA 检测。

匿名模式只需要在 MCP 配置中保留：

```text
ABSTRACT_MODE=deep
FULLTEXT_MODE=enabled
MCP_TRANSPORT=stdio
```

如果需要更高额度，再获取 NCBI API key：

1. 打开 NCBI 账户设置页：

   ```text
   https://account.ncbi.nlm.nih.gov/settings/
   ```

2. 登录或注册 NCBI 账户。
3. 在页面中找到 `API Key Management`。
4. 点击 `Create an API Key` 生成 key。
5. 复制生成的 key；NCBI 通常一个账户同一时间只保留一个 active API key，重新生成会让旧 key 失效。

建议准备两个可选值：

```text
PUBMED_EMAIL=你的邮箱地址
PUBMED_API_KEY=你的 NCBI API key
```

配置建议：

- 匿名测试阶段可以不填 `PUBMED_EMAIL` 和 `PUBMED_API_KEY`。
- 长期或高频使用时，建议填写真实邮箱与 API key，以符合 NCBI E-utilities 使用规范并提高额度。
- `PUBMED_API_KEY` 不要提交到 Git 仓库，也不要写入公开文档或截图。
- 如果 key 泄露，回到 NCBI 设置页删除或重新生成 key，然后更新本地配置。

---

## 3. 安装 PancrePal PubMed MCP

### 3.1 克隆项目

推荐放到用户目录下，避免和本仓库混在一起：

```bash
cd ~
git clone https://github.com/PancrePal-xiaoyibao/mcp-pubmed-server-pancrpal.git
cd mcp-pubmed-server-pancrpal
```

如果你希望放到其他目录，也可以，例如：

```bash
mkdir -p ~/mcp-servers
cd ~/mcp-servers
git clone https://github.com/PancrePal-xiaoyibao/mcp-pubmed-server-pancrpal.git
cd mcp-pubmed-server-pancrpal
```

后续配置中的路径要对应修改。

### 3.2 安装依赖并构建

```bash
npm install
npm run build
```

如果依赖安装或构建失败，先检查：

```bash
node -v
npm -v
pwd
```

### 3.3 可选 `.env` 文件

匿名模式可以不创建 `.env`。如果你希望把 API key 放在 PubMed MCP 项目目录中，可执行：

```bash
cp .env.example .env
```

然后在 `.env` 中填入：

```dotenv
PUBMED_EMAIL=your.name@example.com
PUBMED_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ABSTRACT_MODE=deep
FULLTEXT_MODE=enabled
MCP_TRANSPORT=stdio
```

注意：不同 Agent IDE / MCP server 对 `.env` 加载方式可能不同。最稳妥的方式是在 Agent IDE 的 MCP server `environment` 字段中显式写入必要环境变量；匿名模式只需要非敏感的 `ABSTRACT_MODE`、`FULLTEXT_MODE`、`MCP_TRANSPORT`。

---

## 4. 本地启动测试与稳定 launcher

在 PubMed MCP 项目目录中可以先运行一次终端 smoke test：

```bash
ABSTRACT_MODE=deep FULLTEXT_MODE=enabled MCP_TRANSPORT=stdio node dist/index.js
```

如果看到类似输出，说明 server 可以启动：

```text
PubMed MCP Server ... running on stdio
```

匿名模式下还可能看到类似 `No API keys`、`anonymous mode` 的提示，这是正常的。测试完成后可以按 `Ctrl+C` 停止。MCP 客户端正式调用时，会由 Agent IDE 自动启动这个进程。

ZCode / OpenCode 尤其是 GUI 启动时可能不继承 shell 的 `PATH`，因此长期配置建议使用一个绝对路径 launcher，避免把 MCP 配置写成裸 `node` 后在客户端里找不到 Node.js。

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

请把 `/opt/homebrew/bin/node` 和 `/Users/daxuan/mcp-pubmed-server-pancrpal/dist/index.js` 换成本机真实路径。后续 ZCode / OpenCode MCP 配置优先使用：

```text
/Users/daxuan/.local/bin/pubmed-mcp
```

如果启动失败，优先检查：

1. 当前目录是否是 `mcp-pubmed-server-pancrpal`。
2. 是否已经执行 `npm install` 和 `npm run build`。
3. Node.js 是否为 `18.0.0+`。
4. `dist/index.js` 是否存在。
5. 环境变量是否有不可见空格或中文标点。

---

## 5. 配置到 Agent IDE

### 5.1 不同客户端的配置差异

`zotero-evidence-review` 只依赖“当前会话中可见的 MCP tools”，不绑定某一个客户端。OpenCode、ZCode、Claude Desktop、Cherry Studio 等 Agent IDE 都可以使用，但配置路径和 JSON 结构不相同。

| 客户端 | 常见配置位置 | MCP 配置形态 | 验证方式 |
|---|---|---|---|
| OpenCode | `~/.config/opencode/opencode.json` | 顶层 `mcp`，server 名直接放在 `mcp` 下 | `opencode mcp list` |
| ZCode v2 | `~/.zcode/v2/config.json` | 顶层 `mcp`，server 名直接放在 `mcp` 下 | 完全重启 ZCode 后看工具列表/会话可用工具 |
| ZCode CLI 旧配置/兼容层 | `~/.zcode/cli/config.json` | `mcp.servers` | 取决于实际 CLI/会话读取层 |
| Claude Desktop / 部分 GUI 客户端 | 客户端自己的配置文件 | 常见为 `mcpServers` | 客户端 MCP/server 状态页或新会话工具列表 |

不要把 Claude / Cherry Studio 的 `mcpServers` 示例原样粘贴到 OpenCode 或 ZCode v2；也不要以为 OpenCode 配好了，ZCode 就会自动读取同一个文件。

### 5.2 OpenCode / ZCode v2 顶层 `mcp` 示例

如果你的项目路径是：

```text
/Users/daxuan/mcp-pubmed-server-pancrpal
```

匿名模式配置如下：

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

如果需要把 Zotero MCP 和 PubMed MCP 放在同一个配置中，结构如下：

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

如需 API key，把下面两行加入 `pubmed.environment`：

```json
"PUBMED_EMAIL": "your.name@example.com",
"PUBMED_API_KEY": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### 5.3 ZCode CLI 旧配置/兼容层示例

部分 ZCode CLI 或旧配置可能读取 `~/.zcode/cli/config.json`，并采用 `mcp.servers`：

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

当前桌面版 / v2 ZCode 通常读取 `~/.zcode/v2/config.json`，不是旧 CLI 配置。修改后请完全退出并重启 ZCode。

### 5.4 Claude Desktop / 部分 GUI 客户端

这些客户端常见配置形态是 `mcpServers`，但字段名和启动参数可能随客户端变化。请按对应客户端文档改写，不要把 OpenCode / ZCode 的 `mcp` 片段原样粘贴过去。

---

## 6. 重启与验证

### 6.1 重启会话

修改 MCP 配置后，需要完全重启对应 Agent IDE 或开启新会话，让 MCP 配置重新加载。ZCode 尤其需要确认当前会话已经看到新工具；只刷新聊天通常不够。

### 6.2 查看 MCP 连接状态

OpenCode 可运行：

```bash
opencode mcp list
```

期望同时看到类似：

```text
zotero connected
pubmed connected
```

ZCode v2 没有通用 `zcode mcp list` 命令时，以完全重启后的当前会话工具列表为准：确认出现 `pubmed_search`、`pubmed_get_details`、`pubmed_find_related`、`pubmed_detect_fulltext` 等 PubMed/NCBI 相关工具。

### 6.3 用 skill 做一次小测试

在 ZCode / OpenCode 中输入：

```text
/zotero-evidence-review 搜索 PubMed 和 Zotero 中关于 ATM inhibitor cancer immunotherapy 的文献，列出最相关的 5 篇，并说明证据来源。
```

如果配置成功，报告或聊天结果中 PubMed 状态应为：

```text
PubMed: Completed
```

如果仍然显示：

```text
PubMed: ⚠️ Tool unavailable; search not executed
```

说明当前会话还没有看到 PubMed MCP 工具，需要回到第 5、6 步检查配置路径、JSON 结构和重启。

### 6.4 最小 PubMed MCP 测试 prompt

这是一个 read-only smoke test：只检查当前会话是否能看到并调用 PubMed MCP，不写 Zotero、不下载全文、不清理缓存。

完全重启 ZCode / OpenCode 后，可以直接在新会话中输入：

```text
请测试 PubMed MCP 是否在当前会话可用：
1. 如果能看到 mcp__pubmed__ 相关工具，请先调用 pubmed_system_status。
2. 然后搜索 PubMed：query = "pancreatic cancer chemotherapy"，max_results = 3。
3. 返回每条结果的 PMID、title、year。
4. 明确说明当前会话是否存在 mcp__pubmed__ 工具；如果工具不存在，不要假装搜索成功。
```

成功标准：

- 当前会话工具列表中能看到 `mcp__pubmed__...` 相关工具。
- `pubmed_system_status` 返回系统状态、匿名/API key 状态、fulltext/abstract 模式等信息。
- `pubmed_search` 返回 PMID、标题和年份。
- 如果工具不可见，输出应明确为 `PubMed: ⚠️ Tool unavailable; search not executed`。

### 6.5 Evidence Package 中的 PubMed 状态解释

| 当前会话状态 | Evidence report 应写 | 含义 | RIS 影响 |
|---|---|---|---|
| PubMed 工具不可见 | `PubMed: ⚠️ Tool unavailable; search not executed` | PubMed 扩展层未接入当前会话；不是 Zotero 检索失败 | 不生成 PubMed-only RIS；可给出手动 query |
| 工具可见但未执行，例如明确 chat-only / 非医学主题 | `PubMed: Not executed` 并说明原因 | 有工具但本次工作流没有需要或用户要求跳过 | 不生成 PubMed-only RIS |
| 工具可见但调用报错 | `PubMed: Failed; query reported` | 已尝试 PubMed，但请求失败 | 不生成 PubMed-only RIS；报告 query/error |
| `pubmed_search` 实际运行，且候选 PMID 已用详情/抽取工具检查 | `PubMed: Completed` | 可以把 PubMed 作为已执行证据层 | 仅元数据充分的 PubMed-only 记录可进入 RIS |

注意：只生成 PubMed query、不调用工具，不能算 Completed；只看到工具但没有搜索，也不能算 Completed。

---

## 7. 日常使用教程

### 7.1 普通 PubMed + Zotero 文献搜索

```text
/zotero-evidence-review 搜索 Zotero 和 PubMed 中关于 RMC-6236 resistance mechanism 的文献，列出核心研究，并说明每篇的用途。
```

预期行为：

1. 先查 Zotero 本地库。
2. 自动构造 PubMed query。
3. 调用 PubMed MCP 搜索。
4. 合并结果并去重。
5. 标注来源：`Zotero`、`PubMed` 或 `Zotero + PubMed`。

### 7.2 段落补引用并导出 Evidence Package

```text
/zotero-evidence-review 帮我给下面这段草稿找证据并补引用，生成 Markdown evidence report 和 EndNote RIS：

「ATM inhibition may enhance anti-tumor immunity by promoting cytosolic DNA sensing and cGAS-STING activation, suggesting a potential rationale for combining ATM inhibitors with immune checkpoint blockade.」
```

预期输出文件：

```text
zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_evidence_review.md
zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_references.ris
```

Markdown report 中会包含：

- claim-evidence matrix
- recommended manuscript text
- citation placement
- Zotero search summary
- PubMed expansion
- reference table
- metadata QC
- RIS export status

### 7.3 PubMed related/review discovery

```text
/zotero-evidence-review 先查 Zotero 中 ATM inhibitor immunotherapy 的关键论文，再用 PubMed 查 related reviews 和 similar articles，帮我找最适合综述引言引用的文献。
```

预期行为：

- Zotero MCP 先定位本地已有关键论文、PDF、notes 和 collection 上下文。
- PubMed MCP 对关键 PMID 使用 `pubmed_find_related`，区分 reviews 与 similar articles。
- 报告保留 Zotero 本地链接，同时把 PubMed-only 候选标为 `consider importing` 或 `recommend citing`。

### 7.4 OA/full-text triage

```text
/zotero-evidence-review 对 PubMed 检索到的关键 PubMed-only 文献检查是否有 OA full text；只有可用且必要时再下载全文，用于核实机制证据。
```

预期行为：

- 先用 `pubmed_detect_fulltext` 判断 OA/full-text 可用性。
- 只有在可用、必要且工具启用时才用 `pubmed_download_fulltext`。
- 下载的 PubMed PDF 只视为外部缓存证据，不自动当作 Zotero 本地附件；是否导入 Zotero 需要用户另行确认。

### 7.5 只在聊天中查看，不生成文件

```text
/zotero-evidence-review 只在聊天输出，不要生成文件：帮我分析 RMC-6236 耐药机制有哪些证据，优先使用 PubMed。
```

适合快速探索，不会写出 report / RIS。

### 7.6 深度模式检索肿瘤药物机制

```text
/zotero-evidence-review 使用 PubMed deep mode 搜索 Pan-RAS inhibitor RMC-6236 resistance OR adaptive resistance 的研究，重点总结耐药机制、联合治疗策略和证据等级。
```

建议让 agent 输出：

- 实际 PubMed query
- 命中文献数量
- PMID 链接
- 关键机制
- 是否有临床证据或仅临床前证据
- 是否建议导入 Zotero

### 7.7 获取可导入 EndNote 的 RIS

```text
/zotero-evidence-review 围绕 ATM inhibitor cancer immunotherapy 生成 Evidence Package，并导出 EndNote RIS。PubMed-only 文献只有在元数据完整时才纳入 RIS。
```

注意：

- PubMed-only records 只有在 PubMed MCP 实际检索成功且元数据足够时才会写入 RIS。
- 如果当前 PubMed MCP 工具列表中有 RIS/NBIB/EndNote/BibTeX exporter，优先使用该 exporter 处理 PubMed-only records。
- 如果没有直接 exporter，则用 `pubmed_get_details` 检查后的 PMID 元数据生成 RIS。
- Zotero 和 PubMed 重复文献会按 DOI / PMID / 标题 / 作者年份期刊去重。
- 有冲突的元数据默认应标记为 `Possible metadata mismatch`，不要静默写入 RIS。

---

## 8. 推荐提示词模板

### 8.1 搜索型

```text
/zotero-evidence-review 搜索 Zotero 和 PubMed 中关于 {主题} 的文献，优先纳入近 5 年研究，列出最相关的 10 篇，输出标题、PMID、DOI、研究类型、核心发现和证据来源。
```

### 8.2 机制总结型

```text
/zotero-evidence-review 使用 PubMed deep mode 总结 {药物/机制/疾病} 的研究进展。请展示实际 query，按机制、临床前证据、临床证据、局限性和可引用文献分组。
```

### 8.3 段落补引用型

```text
/zotero-evidence-review 帮我给下面这段论文草稿找证据并补引用，生成 Markdown evidence report 和 EndNote RIS。请先查 Zotero，再用 PubMed 扩展，最后按 PMID/DOI 去重并导出 RIS：

「{粘贴段落}」
```

### 8.4 related/review 发现型

```text
/zotero-evidence-review 基于 Zotero 中已找到的关键 PMID，用 PubMed related/reviews 扩展，找出最适合支持引言背景和机制链条的综述与原始研究。
```

### 8.5 核实主张型

```text
/zotero-evidence-review 请核实以下主张是否被 PubMed / Zotero 文献支持，并按 fully supported、partially supported、not addressed 或 contradicted 分类：

主张：{具体主张}
```

---

## 9. 常见问题

### 9.1 配置后仍显示 PubMed tool unavailable

检查顺序：

1. 是否重启了当前 Agent IDE 会话。
2. 当前使用的是 OpenCode、ZCode v2、ZCode CLI 旧配置还是其他 GUI 客户端。
3. 配置文件路径是否是该客户端实际读取的位置。
4. JSON 形态是否正确：OpenCode / ZCode v2 用顶层 `mcp`；部分旧 ZCode CLI 用 `mcp.servers`；Claude/部分 GUI 常见为 `mcpServers`。
5. `command` 路径是否指向真实存在的 `dist/index.js`。
6. `ABSTRACT_MODE=deep FULLTEXT_MODE=enabled MCP_TRANSPORT=stdio node dist/index.js` 是否能在项目目录中单独启动。
7. 当前会话工具列表中是否出现 `pubmed_search`、`pubmed_get_details`、`pubmed_find_related`、`pubmed_detect_fulltext` 等 PubMed/NCBI 工具。

### 9.2 出现 400 或请求失败

常见原因：

- API key 填错或带空格。
- email 缺失或格式异常。
- query 太复杂或包含不合规字符。
- 请求频率过高。
- PubMed MCP 项目版本变化导致参数名不同。

处理建议：

1. 先用简单 query 测试，例如 `ATM inhibitor`。
2. 降低并发或减少 max results。
3. 如果使用 API key，检查 NCBI API key 是否有效。
4. 查看 PubMed MCP server 的终端错误输出。

### 9.3 是否必须安装 Zotero MCP

如果只想让 AI 搜 PubMed，理论上可以只配置 PubMed MCP。

但本仓库的 `zotero-evidence-review` workflow 推荐同时配置 Zotero MCP，因为它会：

- 优先利用你的本地文献库
- 保留 Zotero item / PDF 链接
- 识别本地已有文献与 PubMed 文献的重复
- 生成更适合写作和 EndNote/Zotero 管理的 Evidence Package

### 9.4 能否把 PubMed MCP 直接装进 skill

不建议，也不符合 MCP 的分层方式。

原因：

- Skill 是提示词/工作流规范。
- MCP server 是独立可执行服务。
- PubMed MCP 依赖 Node.js、npm packages、API key、email、缓存目录和客户端启动配置。
- 把 server 硬塞进 skill 会造成跨平台路径、依赖和密钥管理问题。

正确方式是：

```text
安装 PubMed MCP server → 配置到当前 Agent IDE → skill 在会话中自动调用
```

### 9.5 PubMed-only 文献会自动进 RIS 吗

只有满足以下条件才应进入 RIS：

1. PubMed MCP 实际执行成功。
2. 文献与用户主张高度相关。
3. PMID / DOI / title / authors / journal / year 等元数据足够完整。
4. 没有 unresolved metadata mismatch。
5. 已与 Zotero 结果去重。

否则应只在报告中作为候选或 gap 提示，不写入 RIS。

### 9.6 隐私和 Git 卫生

- 不要把 `PUBMED_API_KEY`、`PUBMED_EMAIL`、`.env`、本机 MCP 私有配置或含真实 token 的截图提交到 Git 仓库。
- `zotero-evidence-output/` 中的报告和 RIS 可能包含未发表稿件、Zotero 本地链接、笔记摘要、检索策略和候选引用；除非明确打算共享，不要提交到公开仓库。
- 公开 issue 或求助时，可保留 tool 名称和错误类型，但应删除 API key、邮箱、本地用户名、私有路径和未发表文本。

---

## 10. 推荐工作流

首次配置：

```text
安装 Node.js → clone PancrePal PubMed MCP → npm install → npm run build → 匿名模式本地测试 dist/index.js → 写入当前 Agent IDE MCP 配置 → 完全重启 Agent IDE → 确认工具列表出现 PubMed tools
```

日常使用：

```text
/zotero-evidence-review → Zotero local search → PubMed expansion → related/review discovery as needed → deduplication → evidence synthesis → PMID/DOI metadata QC → Markdown report + EndNote RIS
```

当 PubMed 不可用：

```text
报告 query → 标注 Tool unavailable → 不生成 PubMed-only RIS records → 修复 MCP 配置后重跑
```
