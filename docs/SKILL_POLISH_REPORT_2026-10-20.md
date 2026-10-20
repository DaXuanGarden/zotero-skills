# Zotero Skills 打磨报告（2026-10-20）

对象：`zotero-evidence-review`、`zotero-manuscript-thinking`、`pubmed-literature-search` 及 Codex 安装流程。

本轮只刨一个面：发布与安装卫生。论文整体思考、领域风格校准、Methods/Results Logic Map 和证据边界协议沿用已验证版本；本轮补的是 Codex 兼容声明、可重复安装、备份去重和首屏安装路径。

## 1. 验料结果

- 真实问题：成立。Zotero MCP 证据检索、全文论文诊断和领域写作校准是稳定的重复任务；当前用户还需要一个不会积累旧副本的安装入口。
- 独特角度：唯一性来自 Zotero 可核验全文、claim/evidence 边界、Methods/Results 对齐和 peer-pattern 校准的组合。
- 安装理由：安装后可用固定入口触发证据审查、全文诊断和 PubMed 扩展；输出包含报告、RIS、Logic Map 和修订优先级。
- 公共传播性：钩子是“用 Zotero 中可核验的同领域论文校准写作决策，再改自己的论证和语言”。可展示产物是 Evidence Package、Domain Style Calibration、Methods/Results Logic Map 和 now-reproducible install check。

结论：好料，继续打磨。

## 2. 访行记录

本轮通过 GitHub API 搜索并阅读了候选仓库首屏、目录或 README。GitHub 是当前可验证的同行来源；ClawHub、skills.sh 和 Tessl 在本轮没有可用的统一检索接口，因此不对它们的排名或覆盖作推断。

| 同类 Skill | 类型 | 可核验信号 | 可学手艺 | 不照搬 |
|---|---|---|---|---|
| [Zotero Analytical Workflow Skills](https://github.com/cheneternity/Zotero-Analytical-Workflow-Skills) | 直接/相邻 | 有 INSTALL、配置样例、tests 和 tools；说明不携带私有库 | 把环境检查、配置和可选依赖写成可运行入口 | Obsidian/MinerU 工作流不是本仓库的默认依赖 |
| [Zotero Research Assistant Skill](https://github.com/Bubble-OoO/zotero-research-assistant-skill) | 直接 | README 给出一句话自动安装、健康检查、测试目录和写入确认门 | 首屏说明 Agent、Zotero、依赖和安全边界 | 它走本地 JSON CLI，不替代 Zotero MCP |
| [zotero-skill](https://github.com/congcongwang0122/zotero-skill) | 直接 | 用一句具体用户请求展示价值，并提供脚本、references 和截图 | 用可见示例降低“装完能做什么”的理解成本 | 不把“一万字综述”承诺写成普遍保证 |
| [Nature-Paper-Skills](https://github.com/Boom5426/Nature-Paper-Skills) | 直接/手艺 | 首屏有 argument-before-style、section contract、examples、evals、安装说明和版本文件 | 用 before/after、行为测试和任务地图证明工作流 | Nature/生命科学规范不能当作跨学科默认 |
| [Academic Writing Skills](https://github.com/WenyuChiou/academic-writing-skills) | 直接 | 明确支持 Codex、Claude Code、OpenCode、Hermes；有 plugin version、CHANGELOG、evals 和 tests | 显式列出 runtime、版本和术语记录 | 插件市场结构不必引入本仓库 |
| [Academic Humanizer](https://github.com/AIScientists-Dev/academic-humanizer) | 手艺 | 有 before/after、伦理边界和“保留数字、引用、claim”的承诺 | 把语言改善和证据保真放在同一首屏 | 不把“humanizer”定位成规避检测工具 |

## 3. 生态位判断

纵向结论：项目已经从 Zotero 检索工具演进为证据驱动的论文修订层；下一阶段应让安装、版本和回滚行为也同样可审计。

横向结论：同类项目更容易被采用的原因集中在四点：一句话安装、可见 before/after、明确 runtime/版本、可验证的安全边界。

交叉洞察：本项目应占据“Zotero 证据边界 + 领域写作校准 + 可复现 Agent 安装”的窄生态位，而不是扩展成泛化论文写作套件。

一句话新定位：**在不改变科学含义的前提下，用 Zotero 全文证据和同领域论文模式改进论文，并让 Codex/OpenCode/ZCode 始终加载同一份可核验版本。**

## 4. 过尺结果

活体与实测证据：

- 仓库静态门禁：`validate-skill.py`、`validate-manuscript-thinking.py`、`validate-pubmed-skill.py` 通过。
- 安装卫生 dry-run：`cleanup-installed-skills.py --target codex` 识别出 28 个时间戳备份，范围只包括本仓库的三个技能。
- 语法与空白：`bash -n scripts/install-skill.sh`、Python 编译检查和 `git diff --check` 通过。
- 当前主副本：三个 Codex 主副本的版本和 SHA 与仓库一致；问题是旧备份副本残留，而不是主副本漂移。
- 运行边界：本轮没有重新执行 Zotero/PubMed MCP 检索；此前报告中的 live fallback 记录仍然有效，本轮分数不把 dry-run 当作真实稿件回放。

| 维度 | 权重 | 得分 | 证据与短板 |
|---|---:|---:|---|
| Frontmatter 与触发条件 | 7 | 7 | 三个 Skill 已声明版本和 Codex/OpenCode/ZCode 兼容性 |
| 工作流清晰度 | 12 | 12 | 证据、全文、风格、Methods/Results 路由已固定 |
| 失败模式编码 | 12 | 10 | MCP 失败、全文 fallback、语料不足有规则；安装错误仍主要依赖命令返回值 |
| 检查点设计 | 6 | 6 | ledger、Logic Map、alignment audit 和安装 drift check 齐全 |
| 可执行具体性 | 17 | 16 | 安装、校验、去重均有可复制命令；真实稿件回放仍需用户材料 |
| 资源整合度 | 4 | 4 | Zotero、PubMed、peer corpus 和清理脚本各有明确边界 |
| 整体架构 | 12 | 11 | 三个互补 Skill 清晰；README 仍较长 |
| 实测表现 | 23 | 17 | 静态验证和安装 dry-run 通过；本轮没有新的 Zotero live replay |
| 反例与黑名单 | 7 | 6 | 保留 claim、数字、引用和安全边界；仍需更多 before/after fixture |
| **总分** | **100** | **89** | 结构和安装卫生已达可发布门槛；真实稿件回放是下一轮主要增益点 |

## 5. 差距清单

### P0

- 真实目标领域和稿件回放仍不足以量化语言校准收益。
- Codex 会话在同步后需要完全重启或开启新会话，当前工具无法替用户刷新已加载的 skill 列表。

### P1

- 继续补一份脱敏的 Introduction 或 Methods/Results calibration card。
- 为公开仓库补一个真实 before/after 示例和可复现 smoke fixture。
- 持续观察 GitHub 同行的版本、evals 和安装入口变化。

### P2

- 增加 `--json` 安装盘点输出，供 CI 或个人仪表盘读取。
- 将 README 的长篇 MCP 配置说明拆到独立指南，保留首屏快速路径。

与同行相比最缺：真实稿件回放、视觉 showcase、跨平台安装市场入口。

最有机会打穿：Zotero 全文证据与写作风格校准的结合、Methods/Results 一致性审计、中文科研用户的 claim-preserving 地道表达。

## 6. 三个打磨方向

### 方案 A：细修（本轮执行）

补齐 Codex 兼容元数据、默认 Codex 安装、备份去重脚本和 drift 门禁。优点是改动小且可直接验证；风险是不会立刻增加真实稿件的语言质量证据。

### 方案 B：精雕

为每次真实回放生成 Domain Style Calibration Card，展示 peer corpus、模式、draft mismatch、safe action 和 claim 对账。优点是更容易人工验收和传播；前提是有脱敏稿件。

### 方案 C：开套件

把风格语料选择与 profile 持久化拆成独立子 Skill。复用性更强，但会增加安装和版本负担；应等方案 B 有稳定使用证据后再做。

推荐顺序：A → B，暂缓 C。

## 7. 本轮改动与验证门

| 文件 | 改动 |
|---|---|
| `scripts/cleanup-installed-skills.py` | 新增默认只读、显式 `--apply` 的安全去重工具 |
| `scripts/install-skill.sh` | 默认目标改为 Codex；新增 `--prune-backups`，安装成功后可清理本仓库旧备份 |
| `scripts/check-installed-skills.py` | 将时间戳备份计入 drift；严格模式会失败并给出同步命令 |
| 三个 Skill frontmatter | 明确声明 Codex / OpenCode / ZCode 兼容性 |
| `README.md` | 增加 Codex 首屏入口、去重规则、安装命令和工具说明 |

验证门：

- [x] `bash -n scripts/install-skill.sh`
- [x] Python 编译检查
- [x] 三个 Skill validator
- [x] cleanup dry-run 识别范围正确
- [x] `git diff --check`
- [ ] 本轮真实 Zotero MCP 回放（需要当前会话工具和目标稿件）

## 8. 执行计划

### 现在完成

- [x] 提交并同步 GitHub。
- [x] 将三个最新 Skill 安装到 Codex。
- [x] 删除 28 个旧时间戳备份并做严格 drift check。

### 下一轮

- [ ] 用指定领域的 3–5 篇 Zotero peer papers 做一轮真实 Introduction 或 Methods/Results 回放。
- [ ] 保存脱敏 calibration card 和 before/after fixture。

## 9. 出师证书

```text
┌──────────────────────────────────────────────┐
│  出师证书 · 鲁班工坊                         │
│                                              │
│  作品：Zotero Skills                         │
│  过尺：86 → 89 / 100                         │
│  定位：Zotero 证据 + 领域写作 + 可复现安装    │
│  绝活：去重、版本、SHA 与 Codex 入口可核验    │
│  下一步：真实稿件回放                         │
│                                              │
│  验收师傅：鲁班                               │
└──────────────────────────────────────────────┘
```

## 10. 回炉清单与参考来源

- 观察 [Nature-Paper-Skills](https://github.com/Boom5426/Nature-Paper-Skills) 的 evals、examples 和版本发布。
- 观察 [Academic Writing Skills](https://github.com/WenyuChiou/academic-writing-skills) 的 Codex/多 runtime 适配和 CHANGELOG。
- 观察 [Zotero Research Assistant Skill](https://github.com/Bubble-OoO/zotero-research-assistant-skill) 的健康检查与写入确认门。
- 观察 [Zotero Analytical Workflow Skills](https://github.com/cheneternity/Zotero-Analytical-Workflow-Skills) 的环境检查与配置可移植性。
- 观察 [Academic Humanizer](https://github.com/AIScientists-Dev/academic-humanizer) 的 before/after 与学术诚信边界。
- 每次更新记录“为什么改、对应哪条回放证据、哪条验证门通过”；不要只记录版本号。
