# Zotero Manuscript Thinking 打磨报告

日期：2026-10-19
对象：`zotero-manuscript-thinking` 及其在 `zotero-evidence-review` 的 Module 2.8 交接
本轮目标：把“整体观 + 领域地道语言 + Introduction/Discussion 逻辑”变成可触发、可核验、可交接的写作工作流。

## 1. 验料结果（Skill 前提挑战）

挑战1 - 真实问题：**成立**。局部润色容易让句子变顺，却让研究问题、贡献、证据边界和章节角色继续漂移；用户还需要一个能“抬头看全文”的 checkpoint。

挑战2 - 独特角度：唯一性来自 **Zotero 证据工作流 + manuscript-level argument spine + 领域语料校准** 的组合。原来的整体诊断已经有方法论优势，本轮补上了“地道”这一容易凭感觉判断的部分。

挑战3 - 安装理由：装好后，用户可以用一句话触发全文诊断，得到 paper contract、Language Audit、Introduction/Discussion Logic Map、claim–evidence–section map、Domain Style Calibration 和 P0–P3 修订顺序。它比临时要求“帮我润色”更稳定，因为会记录 scope、未读材料、证据层和停止条件。

挑战4 - 公共传播性：一句话钩子是“**先用同领域可核验论文校准写作决策，再改自己的句子；不复制原文，也不让语言变漂亮后偷偷变强**”。当前可展示产物是结构化诊断报告和 peer-pattern 对照表；仍缺真实论文回放 GIF/截图。

验料结论：**好料，继续打磨**。

## 2. 访行记录（同类 Skill 横向对标）

| 同类 Skill | 链接 | 类型 | 一句话定位 | 它为什么容易被理解/安装/传播 | 可学的手艺 | 不能照搬的点 |
|---|---|---|---|---|---|---|
| Nature-Paper-Skills | [GitHub](https://github.com/Boom5426/Nature-Paper-Skills) | 直接同行 | 以证据、读者和 section contract 驱动的生命科学论文工作流 | 首屏讲清“argument before style”、目标 venue、真实 first-run 示例；安装和任务入口很具体 | 先定义 section contract/reader，再润色；用真实 before/after 和行为测试 | Nature 风格和生命科学语料不能直接变成所有学科的默认规范 |
| Horizon Academic Writing | [GitHub](https://github.com/yujie-jason-zhang/horizon-academic-writing) | 直接同行 | 分层处理段落润色、全文对齐和科学审计 | 把 Ember/Afterglow/Aurora/Aegis 的边界说清，强调 cross-section claim alignment 和 fidelity verification | 将“局部润色”和“全文一致性”分成不同能力；提供 diagnosis/verification 模式 | 其 LaTeX/英文工作流和本仓库的 Zotero/PubMed 依赖不同 |
| Embodied AI Paper Writer | [GitHub](https://github.com/OpenGHz/embodied-ai-paper-writer) | 直接/领域同行 | 从 63 篇顶会论文提取具身智能写作模式和 phrasebook | 明确 corpus 数量、venue、playbook、phrasebook 和可追溯 research files；规则能落到句式/段落/图表 | 把“像领域论文”具体化为 corpus-tuned patterns，并区分模式学习与内容建议 | 具身智能的 63 篇论文不能代表医学、流行病学或其他领域 |
| Scholar Forge | [GitHub](https://github.com/hyl-ailab/scholar-forge) | 间接同行 | 用模式路由串联文献、IMRaD、学位论文、基金、审稿和修回 | 以“一个 Skill，完整学术生命周期、诚信优先、中英双语”作为清晰定位，并配验证脚本 | 借鉴统一路由、中文场景和 claim–evidence mapping 的产品叙事 | 一体化套件复杂度更高；不应把当前 Skill 扩成无边界大套件 |
| Research Paper Lifecycle Skills | [GitHub](https://github.com/ShaishavMaisuria/research-paper-lifecycle-skills) | 间接同行 | 覆盖论文从发现、写作、验证到投稿、rebuttal 和展示的生命周期 | README 有真实产物、快速安装、边界声明、venue rules 和网站入口 | 学习“可见产物优先”、明确不会做什么、将 venue 规则和验证结果分开 | 其 field-agnostic 生命周期范围远大于本 Skill 的 manuscript checkpoint |
| Medical Research Agent Skills | [GitHub](https://github.com/aipoch/medical-research-skills) | 手艺同行 | 大规模医学研究 Skill 库，覆盖证据、设计、分析和写作 | 有 500+ skills、医学分类、MedSkillAudit 和 demo，首屏信号强 | 学习 domain-specific audit、阶段化目录和“谁会用”表达 | 数量和品牌信号不能替代一个具体 Skill 的真实回放质量 |
| qinyan-academic-skills | [GitHub](https://github.com/LeonChaoX/qinyan-academic-skills) | 手艺同行 | 多语言、端到端学术研究 Skill 集合 | 用“182 个可安装 Skill”与研究阶段目录降低发现成本 | 学习分类、入口和多语言说明 | 大型集合的规模不应诱使本 Skill 增加无关功能 |

## 3. 生态位判断

纵向结论：本项目已经从 Zotero 段落证据检索，演进到“证据驱动的论文修订决策层”；下一阶段应把语言校准从原则升级为可追踪的 peer corpus 流程。

横向结论：同类项目的优势主要来自三件事：可见的真实产物、明确的层级/边界、可追溯的领域语料或规则。当前仓库的证据边界和验证脚本较强，真实写作回放和领域 corpus 资产仍弱。

交叉洞察：真正值得抢的生态位不是“又一个 AI 润色器”，而是 **Zotero 证据和同领域写作语料之间的 manuscript-level calibration layer**。

一句话新定位：**在不改变科学含义的前提下，用全文论证检查和可核验的同领域论文模式，把“语言要地道”变成可解释、可回溯的修订决策。**

## 4. 过尺结果（活体检查 + 九维评分）

活体检查记录：

- 结构尺：Luban `check-skill-repo.sh .` 完成，7 项 PASS、7 项 WARN、0 项 FAIL。WARN 主要是仓库级公开发布资产缺失：LICENSE、`.claude-plugin/marketplace.json`、demo GIF、`npx skills add` 和 skills.sh 徽章。
- 实测尺：`python3 scripts/check-all.py --output-warnings skip --smoke-prompts check` 通过；三个 Skill validator、literature writer self-test 和 smoke prompt guardrail 均通过。
- 安装对账：`python3 scripts/check-installed-skills.py --target codex --mode fail` 通过；Codex 副本已同步到 `0.4.0` / `3.0.0`，并保留备份。
- 真实 Zotero MCP：已完成一轮只读链路回放。`zotero_get_recent(limit=3)` 和 `zotero_semantic_search(...)` 成功；候选 `79DNZ7M9` 的 metadata、PDF attachment discovery 和 full-text fallback 成功。其 PDF attachment `P9VEZ8VG` 的 outline/page endpoint 返回 502，因此按规则标记为 `fulltext fallback`，没有把它误报为 page-level PDF inspection。第二个候选 `RR8UW3HP` 也复现了相同的本地 PDF endpoint 边界。
- 输出新鲜度：仓库中的 Zotero 产物最近一份为 2026-09-25，其余多为 2026-06-19 至 2026-06-22；这些是历史证据包，不足以证明新的 manuscript-thinking 活体效果。

本次 live replay 的可审计记录：

| Peer ID | Zotero item / attachment | 检查结果 | 可用证据 | 风格校准结论 |
|---|---|---|---|---|
| P1 | `79DNZ7M9` / `P9VEZ8VG` | metadata、child attachment 和 `zotero_get_item_fulltext` 成功；outline/page 返回 502 | 全文 fallback 中可定位 Introduction、Step 1–3 和 Discussion 相关段落；page-level location unavailable | 只能作为链路和 fallback 验证，不能单独支撑领域共识 |
| P2 | `RR8UW3HP` / `VEDXE7I2` | metadata、child attachment 成功；outline 复现本地 PDF endpoint 502 | 未继续把 attachment metadata 当作正文证据 | `metadata-only / page unavailable` |

P1 的全文中可观察到“先定义整体任务，再按阶段展开，再给出可执行动作”的结构模式；由于当前没有用户指定的目标领域、文章类型和稿件段落，本轮不把它写成医学/生物医学领域的语言规范，也不生成 copy-ready 改写。

| 维度 | 权重 | 得分 | 主要证据 | 最大短板 | 优先级 |
|---|---:|---:|---|---|---|
| Frontmatter 与触发条件 | 7 | 6 | 有版本、父 Skill、全文/语言/Introduction/Discussion 触发词和非触发条件 | frontmatter 没有完整负触发字段；主要边界在正文 | P2 |
| 工作流清晰度 | 12 | 12 | meaning gate、Methods/Results/Introduction/Discussion section logic、style calibration、argument spine、evidence/consistency 的顺序明确 | 仍需用真实稿件验证负担是否适中 | P1 |
| 失败模式编码 | 12 | 10 | 覆盖 overclaim、Unsupported gap、引用归属、段落失焦、语料不足和不可用工具 | 领域风格的错误选择还没有自动检测器 | P1 |
| 检查点设计 | 6 | 6 | scope ledger、paper contract、claim map、reviewer stress test、stop conditions | — | P2 |
| 可执行具体性 | 17 | 16 | 输出字段、Methods/Results Logic Map、Methods–Results alignment、动作类型、Done when、peer corpus ledger 和 confidence 已固定 | 选文与模式抽取仍由 Agent 手工执行 | P1 |
| 资源整合度 | 4 | 3 | 新增 `references/domain-style-calibration.md`，并向 writing-core/medical editor 传递 profile | 尚无可复用的领域 corpus 包 | P1 |
| 整体架构 | 12 | 11 | 子 Skill 与父 Skill Module 2.8、Methods/Results 专用交接、安装脚本、README、validator 已对齐 | 入口文档偏长，后续可拆分更多 references | P2 |
| 实测表现 | 23 | 17 | 静态 validator、安装副本、安全 smoke 和一轮真实 Zotero 检索→metadata→attachment→full-text fallback 通过 | 仍没有真实稿件的 before/after，也没有成功的 page-level PDF 读取 | P0 |
| 反例与黑名单 | 7 | 5 | 不复制原文、不把高分当事实、语料不足降级、不改变 claim strength | 缺少真实 before/after 反例集 | P1 |
| **总分** | **100** | **86** | 结构、静态检查、Methods/Results 章节协议和一轮真实 Zotero 链路完成；稿件级回放仍未完成 | 真实稿件 before/after 与多篇 peer corpus 回放是下一轮最大杠杆 | **P0/P1** |

## 5. 差距清单

### P0：不补就无法证明有效

- 没有一组真实稿件 + Zotero peer corpus 的回放，无法证明 Domain Style Calibration 比普通语言润色更好。
- 当前 smoke prompt 只验证路由和安全措辞，没有验证“选文 → 模式抽取 → 对照表 → copy-ready 文本”的真实产物链。

### P1：补上后明显提升可信度和使用价值

- 增加一个真实（可脱敏）Introduction 或 Discussion 回放，至少记录 3 篇 peer paper、3 个 pattern、2 个 draft mismatch 和修改前后 claim-strength 对账。
- 将 peer corpus 选择标准和 `calibration_confidence` 固化为可检查 JSON/Markdown fixture，避免每次靠自由发挥。
- 增加 venue/genre mismatch 反例：同一段落在医学原始研究、综述和会议论文中不能共用同一套“地道”模板。
- README 仍缺出生证中的 `npx skills add`、真实 demo、LICENSE 和 marketplace 双通道；若面向公开生态，这些会阻断转化。

### P2：锦上添花

- 为中文、英文和中英转换分别增加术语/连接词/claim verb 的小型 pattern schema。
- 在全文报告中增加“稳定术语表”和“贡献 noun phrase”跨章节回收表。
- 让父 Skill 的 checkpoint 在多轮修改之间持久化 `claim IDs` 和 style profile。

### 与同行相比，我们最缺的3件事

1. 可复现的真实写作回放和 before/after 产物。
2. 可公开审查的领域语料包或 fixture。
3. 首屏安装/展示资产（GIF、示例、标准安装入口）。

### 与同行相比，我们最有机会打穿的3件事

1. 把 Zotero 证据边界和写作风格校准放进同一条可追踪链。
2. 中文科研用户的“地道但不口语化”需求，以及中英转换的 claim-preserving 约束。
3. 将全文 checkpoint 的 P0/P1 决策直接交接给 citation、claim audit、Introduction/Discussion polisher。

## 6. 三个打磨方向

### 方案A：细修——把当前 Skill 做成可信的领域校准器（推荐）

新定位：保留单 Skill + parent Module 2.8，补 peer corpus ledger、真实回放 fixture、术语/claim verb 一致性和 venue mismatch 反例。
优点：改动小、容易验证、不会打散当前 Zotero 证据工作流。
风险：不同学科的语言模式仍需逐步累积。
适合条件：先服务当前医学/生物医学论文场景。

### 方案B：精雕——做出可见的“风格校准卡”

新定位：每次运行生成一张 `Domain Style Calibration Card`，包括目标 profile、peer corpus、5 个观察模式、confidence、2 个改写前后对照和不采用项。
优点：传播和人工验收都更强；能让用户一眼看到“为什么这样改”。
风险：需要真实稿件和可展示的脱敏样例。
适合条件：用户愿意提供一个可公开或可脱敏的段落回放。

### 方案C：开套件——拆出独立的 `zotero-domain-style-calibration` 子 Skill

新定位：独立负责选文、风格模式抽取和 profile 持久化，`zotero-manuscript-thinking` 只负责调用。
优点：模块复用更强，可为不同领域维护独立 corpus。
风险：安装、路由、版本和维护成本上升；需要先证明方案A 的真实调用频率。
适合条件：至少有两个不同领域用户/项目需要同一套校准流程。

推荐选择：**方案A → 方案B**。先用真实回放证明有效，再做风格校准卡；暂缓方案C，避免过早扩大 Skill 套件。

## 7. 本轮候选改写与验证

本轮只刨：**领域地道语言校准这一面**。全文 checkpoint、证据边界和下游 handoff 保持原有主线。

已落地：

| 文件 | 变更 | 目的 |
|---|---|---|
| `zotero-manuscript-thinking/SKILL.md` | 版本 `0.4.0`；加入 Methods/Results 逻辑协议、可复现性与结果叙事审计、section-specific style calibration、专用叶子 Skill 交接，并保留 Zotero MCP 顺序、语料门禁和 PDF 错误解析规则 | 让“地道”同时服务方法可复现和结果可读性 |
| `zotero-manuscript-thinking/references/domain-style-calibration.md` | 新增目标定义、3–5 篇选文、Zotero PDF 片段读取链、模式抽取、对照表、confidence 和停止规则 | 将执行细节从入口文档中分离并可复用 |
| `zotero-evidence-review/SKILL.md` | 版本 `3.0.0`；Module 2.8 加入 Methods/Results Logic Map、Methods–Results alignment 和专用 handoff，同时保留 style corpus ledger、Zotero Style Evidence Ledger、parent-key/fallback/error parsing 规则 | 保证父 Skill 路由与子 Skill 一致 |
| `scripts/validate-manuscript-thinking.py` | 增加 reference、confidence、反复制 guardrail 检查 | 防止文档回退 |
| `scripts/smoke_prompts.py` | 新增 domain-style-calibration dry run | 验证路由和安全边界 |
| `README.md` / `docs/SKILL_IMPROVEMENT_PLAN.md` | 增加用户入口、版本和设计原则 | 让能力可发现、可解释 |

关键可直接替换片段：

```text
如果用户要求“像本领域高水平论文一样自然”，先定义 domain、article_type、target_venue、section 和 audience；再从 Zotero 优先选择 3–5 篇可检查的匹配论文，记录选择理由和访问状态，抽取 rhetorical moves、claim verbs、术语、citation ownership 和信息节奏。输出 peer pattern → draft mismatch → safe action → meaning check；没有至少三篇匹配语料时标记 low/none，不把模型直觉或单篇论文习惯称为领域规范。
```

验证门结果：`validate-manuscript-thinking.py`、`check-all.py --output-warnings skip --smoke-prompts check`、`git diff --check`、Codex 安装副本对账均通过；真实 Zotero/PubMed live replay 尚未通过验证门，因此本轮实测分数保守计入。

## 8. README 与 Showcase 升级建议

- 首屏保留“整体论文 + 领域地道语言”双钩子，并把 `Domain Style Calibration` 结果卡放到安装命令前。
- 增加一个可脱敏的真实示例：`draft paragraph → 3 peer papers → 5 patterns → comparison table → copy-ready paragraph`。
- 公开发布前补 `LICENSE`、`.claude-plugin/marketplace.json`、`npx skills add`、skills.sh badge 和可复现 demo 脚本。
- 在示例旁明确写“peer papers provide patterns, not claims”，避免用户理解成抄袭或自动寻找“高分句子”。

## 9. 执行计划

### 24小时内必须完成

- [x] 把领域风格校准协议写入子 Skill 和父 Skill Module 2.8。
- [x] 增加静态验证和安全 dry-run prompt。
- [x] 同步 Codex 安装副本并做 drift check。

### 3天内完成

- [ ] 选择一个真实医学论文段落，建立 3–5 篇 peer corpus，跑一轮人工验收。
- [ ] 保存一份脱敏的 `Domain Style Calibration Card` fixture，并把它加入回放测试。
- [ ] 对照真实回放更新 80 分中的“实测表现”和“反例”分数。

### 7天内完成

- [ ] 根据回放结果决定是否增加领域 corpus pack 或 venue profile。
- [ ] 若要公开发布，再补出生证中的安装、LICENSE、marketplace、demo 和 skills.sh 资产。

### 本轮不做

- 不创建独立的 `zotero-domain-style-calibration` 第三个 Skill。
- 不把某个期刊/会议的格式规则写成跨学科通用规则。
- 不做 merge、tag、release 或任何外部发布动作。

## 10. 出师证书

```text
┌──────────────────────────────────────────────┐
│  出师证书 · 鲁班工坊                         │
│                                              │
│  作品：zotero-manuscript-thinking            │
│  过尺：当前 80 / 100                         │
│        （结构 + 静态实测；live replay 未完成）│
│  定位：Zotero 证据边界与领域写作校准层       │
│  绝活：peer pattern → draft mismatch        │
│        → safe action → meaning check         │
│  下一步：用真实稿件完成一轮可复现回放         │
│                                              │
│  验收师傅：鲁班                               │
└──────────────────────────────────────────────┘
```

## 11. 回炉清单

- 持续观察 [Nature-Paper-Skills](https://github.com/Boom5426/Nature-Paper-Skills) 的行为测试和 section evidence 更新。
- 持续观察 [Horizon Academic Writing](https://github.com/yujie-jason-zhang/horizon-academic-writing) 的 fidelity/consistency checker 设计。
- 持续观察 [Embodied AI Paper Writer](https://github.com/OpenGHz/embodied-ai-paper-writer) 的 corpus、phrasebook 和 playbook 更新。
- 持续观察 [Research Paper Lifecycle Skills](https://github.com/ShaishavMaisuria/research-paper-lifecycle-skills) 的 live venue rules、产物和兼容 runtime。
- 每次回炉保留 release note：为什么改、对应哪条真实回放问题、哪条验证门通过。
- 下一轮入口固定为：真实段落、目标领域/venue、3–5 篇 peer papers 或 Zotero 检索条件、作者不允许改变的术语/结果/claim boundary。

## 12. 需要用户确认的问题

1. 下一轮真实回放优先选哪个领域/目标 venue？如果未指定，默认从当前医学/生物医学稿件开始。
2. 是否有一个可以脱敏的 Introduction 或 Discussion 段落，用于生成第一张 `Domain Style Calibration Card`？

## 13. 附录：参考来源

- [Nature-Paper-Skills](https://github.com/Boom5426/Nature-Paper-Skills)
- [Horizon Academic Writing](https://github.com/yujie-jason-zhang/horizon-academic-writing)
- [Embodied AI Paper Writer](https://github.com/OpenGHz/embodied-ai-paper-writer)
- [Scholar Forge](https://github.com/hyl-ailab/scholar-forge)
- [Research Paper Lifecycle Skills](https://github.com/ShaishavMaisuria/research-paper-lifecycle-skills)
- [Medical Research Agent Skills](https://github.com/aipoch/medical-research-skills)
- [qinyan-academic-skills](https://github.com/LeonChaoX/qinyan-academic-skills)
