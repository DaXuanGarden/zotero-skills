# Skill 打磨报告（2026-10-24）

## 1. 验料结论

三个核心 Skill 都值得继续打磨，且分工已经成立：

- `zotero-literature-learning` 收集、筛选、阅读并抽取可迁移素材；
- `zotero-manuscript-thinking` 先看全文主线、章节逻辑和领域语言，再排修订优先级；
- `zotero-evidence-review` 把具体主张落到可检查证据、引文核实和 RIS。

本轮真正的短板不是功能不足，而是三层之间容易重复检索、摘要层证据容易被误当作全文语言依据、局部改写完成后缺少统一的回查记录，以及“找到一篇能支持”被误当作“检索已经充分”。

## 2. 访行记录

| 项目 | 链接 | 类型 | 可学手艺 | 不照搬 |
|---|---|---|---|---|
| zotero-mcp | https://github.com/54yyyu/zotero-mcp | 直接同行 | 明确区分库检索、全文读取和对话入口 | 不把通用问答当作本文的证据/写作交接 |
| zotero-mcp plugin | https://github.com/cookjohn/zotero-mcp | 直接同行 | 将 Zotero 元数据、全文和 MCP 能力写成清楚的用户入口 | 不引入与本仓库无关的写入操作 |
| research-workflow-assistant | https://github.com/Intersect-Collaborations-LLC/research-workflow-assistant | 间接同行 | 阶段化、可审计、跨来源的研究工作流 | 不把外部数据库扩展成 Zotero 本地证据的替代品 |
| claude-academic-workflow | https://github.com/ericluo04/claude-academic-workflow | 间接同行 | 用多个小 Skill 分担研究、写作、审计和质量门 | 不无限拆 Skill；本仓库保留三层主线 |
| quill | https://github.com/iamsikun/quill | 手艺同行 | 首屏承诺保留 claims、numbers、notation、citations | 不把“润色”写成无需证据的自动改写 |
| manuscript-writing | https://github.com/YSLAB-ai/manuscript-writing | 手艺同行 | 把学术改写、引用和清晰度检查放进一个可安装入口 | 不把不同证据层级混成单一评分 |
| personal-academic-writing-skill | https://github.com/Jingyang-Zhu/personal-academic-writing-skill | 手艺同行 | 从目标语料抽取可复用的作者风格 profile | 不复制 peer paper 原句或把个体习惯写成领域规范 |

交叉结论：本项目最适合占据“Zotero 全文证据驱动的论文素材学习—全文思考—具体证据修复”这一生态位。可传播的钩子是：**先从自己的 Zotero 全文学习同领域写作决策，再把每个改动回查到证据、章节和主张边界。**

## 3. 过尺结果

| Skill | 基线 | 本轮后 | 主要证据 |
|---|---:|---:|---|
| `zotero-evidence-review` | 88/100 | 93/100 | 路由契约、单一 owner、source layer/inspection status/stop reason 进入输出约束；原有 Zotero/PubMed 顺序与 RIS 门禁通过 |
| `zotero-literature-learning` | 86/100 | 92/100 | 新增 evidence/style/argument 三种用途门禁、`learning_decision` 和可执行的 `learning_decisions.md` |
| `zotero-manuscript-thinking` | 87/100 | 94/100 | 固化 meaning → logic → peer calibration → language → audit 顺序；增加 Methods/Results 词义—证据职责表和 `POST_WRITE_AUDIT` |

### 后续检索与 EndNote 交接打磨

`zotero-evidence-review` 已升级到 **3.2.1**。本次增量把检索和导入边界进一步写实：

- 段落证据请求按 claim block 拆解，分别运行 Zotero semantic、Zotero structured、PubMed broad、PubMed design/method 和必要的 PubMed related lanes；
- 用 `Recall Audit` 记录 raw hits、unique candidates、direct-support candidates、coverage gaps 和饱和停止理由；两轮没有新 direct-support candidate 才能停止，不能因找到一篇支持文献就停止；
- 最终仍只生成一个 canonical RIS，保留 `Zotero` / `PubMed` / `Zotero + PubMed` 来源 provenance；
- 新增 `ZOTERO_IMPORT_HANDOFF` 与 `ENDNOTE_IMPORT_HANDOFF`。PubMed-only 记录保留 DOI/PMID 和 `zotero_import_status: pending`，只有用户明确要求时才通过 DOI 导入 Zotero、刷新搜索索引并重新读取真实 item key；不得伪造 `zotero://select/items/...`。`format-references-endnote`、`endnote-workflow` 和 `bib-formatter` 被定义为下游文档/格式工具，不直接修改 EndNote 文库；实际 `.enl/.Data` 导入由用户在 EndNote 中确认。

评分是仓库维护用的相对尺，不是论文质量或投稿接受率预测。静态质量门全部通过；真实 Zotero 活体检查中 `zotero_get_recent`、语义检索、metadata、children 和 fulltext fallback 成功，PDF outline 调用返回 502，因此按规则记录为失败并使用已声明的 fulltext fallback，没有把它误报成页级 PDF 检查。

## 4. 本轮改动

### `zotero-evidence-review` 3.1.0

- 新增 `Route contract: one request, one evidence owner`，明确 search/learn/support/verify/think 的 owner、交接和停止条件；
- 要求报告记录 `route`、`source_layer`、`inspection_status`、`claim_ids`、`output_files` 和 `stop_reason`，减少重复文献出口；
- 保留并复用既有 Zotero-first、PubMed 可见时扩展、顺序调用、RIS canonicalization 和当前研究/外部证据分层。

### `zotero-literature-learning` 0.3.0

- 新增 `evidence_usable`、`style_usable`、`argument_usable` 三个素材用途门禁；
- 新增 `learning_decision` 记录，把 peer observation 转成安全动作、意义回查、下一个 owner 和 `done_when`；
- `MATERIALS_PACKAGE` 新增 `learning_decisions.md`，让素材包可以直接驱动下一步写作或证据修复；
- schema 同步增加候选用途、检查依据、下一动作和学习决策字段。

### `zotero-manuscript-thinking` 0.5.0

- 固化“先保意义，再校准领域语言”的五步修订顺序；
- 对 `annotation`、gene/tissue/pathway analyses、enrichment、prioritize 和 claim verbs 增加动作—术语—证据职责校准；
- 输出契约新增 `Revision Decision Log` 和局部改写后的 `POST_WRITE_AUDIT`，强制回查主张、数字、引用归属和 Methods–Results 对齐。

## 5. 验证记录

已运行并通过：

```text
python3 scripts/check-all.py --output-warnings skip --smoke-prompts check
python3 scripts/check-installed-skills.py --target codex --mode fail
```

其中包含四个 Skill validator、literature package writer self-test 和 smoke prompt guardrail。安装同步后应再次运行 installed drift check；本报告不把静态通过写成 MCP 全链路通过。

## 6. 回炉清单

下一轮只在真实用户任务中观察三项：

1. `MATERIALS_PACKAGE` 是否真的被下游消费，而不是重新检索同一主题；
2. `Domain Style Calibration` 的 peer pattern 是否能减少改写轮次；
3. `POST_WRITE_AUDIT` 是否能抓到 Methods/Results 术语或证据强度漂移。
4. `Recall Audit` 是否能在真实段落检索中减少漏检，同时保持最终 RIS 简洁。

本地 `zotero-evidence-output/gsmr_parameters_2026-09-25_225257/` 是旧的未跟踪运行产物，未删除、未提交，也未用于公开示例。

## 出师证书

```text
┌──────────────────────────────────────────────────────────────┐
│  鲁班出师：Zotero writing workflow v2026-10-24               │
│  三 Skill：route 清楚 · 素材可追溯 · 改写可回查 · 检索可审计  │
│  静态质量门：PASS                                             │
│  活体 Zotero：search/metadata/fulltext fallback 已核验       │
│  未完成项：PDF outline 502 已按 fallback 规则记录            │
└──────────────────────────────────────────────────────────────┘
```
