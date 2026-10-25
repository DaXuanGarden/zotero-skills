# Zotero Evidence Review Skill 打磨报告（2026-10-25）

## 1. 验料结果

挑战1 - 真实问题：成立。用户需要在真实稿件中快速判断“这篇文献支持哪一句话、插在哪里、如何在 Zotero/EndNote 中找到”。

挑战2 - 独特角度：来自 claim-level evidence mapping、中文主张摘要、手动插引路径、证据边界校准和 RIS 交接的组合工作流。

挑战3 - 安装理由：安装后可得到可直接粘贴的英文稿件、紧随正文的中文主张—证据矩阵和可执行的插引清单，减少作者在报告、Zotero 和 EndNote 之间来回跳转。

挑战4 - 公共传播性：一句话钩子是“把一段英文稿件变成可粘贴、可解释、可插引、可审计的证据包”。可展示产物是正文 → 中文矩阵 → 插引清单三屏路径。

验料结论：好料，继续打磨。

## 2. 访行记录

| 同类项目 | 链接 | 类型 | 可学手艺 | 本 Skill 的差异 |
|---|---|---|---|---|
| scholar-support | <https://github.com/mcmespinaa/scholar-support> | 直接/间接 | 首屏说明用户下一步和引用审计 | 本 Skill 额外提供 Zotero 本地证据链、中文主张摘要和 RIS 交接 |
| research-paper-lifecycle-skills | <https://github.com/ShaishavMaisuria/research-paper-lifecycle-skills> | 间接 | 把论文工作拆成可复用阶段 | 本 Skill 聚焦段落级证据与实际插引，不扩展成整套写作平台 |
| AI Citation Auditor | <https://github.com/SahPet/ai-citation-auditor> | 直接 | 可见的 citation audit 表和 split-support 解释 | 本 Skill 把审计信息和作者插引路径分层 |
| EndNote for Word | <https://github.com/felimet/endnote-for-word> | 手艺 | 明确导入、搜索和编号交接 | 本 Skill 输出 EndNote-compatible RIS，同时保留 claim-level 证据判断 |
| Scholar Forge | <https://github.com/hyl-ailab/scholar-forge> | 手艺 | 结果导向的研究工作流展示 | 本 Skill 把结果固定为正文、矩阵和操作表 |

## 3. 生态位判断

纵向结论：Skill 已从“搜索文献”发展为“段落证据包”，下一阶段重点是让作者更快完成人工插引并减少表格重复。

横向结论：同类项目更容易被理解的共同点是首屏给出行动路径、明确审计边界、提供可见产物。

交叉洞察：真正应占据的生态位是“作者手动插引前的证据交接层”，连接 Zotero/PubMed 证据、英文润色和 Word/EndNote 操作。

一句话新定位：**把英文段落变成可粘贴、可解释、可插引、可审计的 Zotero 证据包。**

## 4. 过尺结果

| 维度 | 权重 | 得分 | 主要证据 | 最大短板 |
|---|---:|---:|---|---|
| Frontmatter 与触发条件 | 7 | 7 | v3.9.0、Codex/OpenCode/ZCode 兼容性、依赖声明；静态验证通过 | 仍依赖 Zotero MCP 运行时连接 |
| 工作流清晰度 | 12 | 12 | 唯一报告布局、三步手动插引路径、作者先读正文和矩阵 | 长篇审计附录仍需折叠阅读 |
| 失败模式编码 | 12 | 12 | PubMed truth boundary、未核验记录排除、单一 A–E 等级规则 | 真实 MCP 断连仍需运行时处理 |
| 检查点设计 | 6 | 6 | pre-write/post-write QA、Citation Package validator | 语义支持仍需人工判断 |
| 可执行具体性 | 17 | 17 | `search_tokens`、`copy_ready_citation`、`insertion_anchor`、Manual action | 期刊特殊引用样式仍需用户提供 |
| 资源整合度 | 4 | 4 | 新增 `references/report-layout.md`，更新 citation handoff validator | 生态对标仍是外部链接清单 |
| 整体架构 | 12 | 12 | 正文、矩阵、插引表、审计附录职责分层 | 历史输出包仍保留旧格式 |
| 实测表现 | 23 | 17 | insomnia–MASLD 包通过 report/RIS validator；仓库 check-all 全绿 | 本轮是版式重排，未重新执行全套 MCP 检索 |
| 反例与黑名单 | 7 | 7 | A/B、A/C 等混合等级禁用；Yuan/Tan 未核验不进入正文/RIS | 未来需继续收集边界案例 |
| **总分** | **100** | **94** | 静态、包级和安装漂移检查均通过 | 运行时语义核查仍需单独执行 |

## 5. 差距清单与本轮改动

### P0

- 报告作者路径不够单一：已新增 `references/report-layout.md`，固定为 Metadata → Warnings → Copy-ready → Claim–Evidence Matrix → Citation Insertion Sheet → Annotated/Diff → Audit Appendix。
- Claim–Evidence Matrix 缺少中文主张摘要：已新增 `主张摘要（中文）` 列并写入输出模板和审计规则。
- 混合证据等级造成歧义：已禁止 `A/B`、`A/C`、`C/D` 等复合值，要求拆分 claim 或采用最保守单一等级。

### P1

- 三张表职责重叠：已把 `SENTENCE_CITATION_MATRIX`、Citation Support Ledger、完整元数据收进审计附录。
- 手动插引步骤不够显眼：README 和报告均固定为三步路径，并保留 `search_tokens` 与 `copy_ready_citation` 的区分。
- 静态审计器无法正确识别多级标题：修复 `evidence_output_audit.py` 的多行标题解析，并支持 `Manual action`。

### P2

- 历史输出仍有旧布局：保留历史记录，后续新包按 v3.9.0 布局生成。
- 运行时 MCP 证据仍受连接状态影响：继续保留断连和 PubMed 不可用的明确状态词。

## 6. 活体与验证记录

- `python3 scripts/check-all.py --output-warnings skip`：通过。
- `python3 scripts/validate-skill.py`：通过，v3.9.0。
- `validate-citation-package.py`：insomnia–MASLD 报告与 RIS 通过。
- `evidence_output_audit.py`：当前 insomnia–MASLD 包无自动警告。
- `ris_lint.py`：当前 insomnia–MASLD RIS 无警告。
- `check-installed-skills.py --target codex --mode fail`：仓库与 Codex 安装副本 SHA256 一致。
- GitHub 提交：`9688efe Improve evidence report layout and citation handoff`。

## 7. 回炉观察清单

- 下一次真实段落任务：记录作者从正文到插入第一条引文所需的步骤数和返工次数。
- 观察矩阵中文摘要是否能减少作者打开审计附录的次数。
- 收集不同期刊的 author–year 和 numbered Vancouver 样式，验证 `copy_ready_citation` 与 EndNote 编号交接。
- 运行一次 Zotero 断连和 PubMed 不可用的活体测试，确认报告仍保持同一布局和状态词。

## 8. 出师证书

```text
┌──────────────────────────────────────────────────────────────┐
│                    LUBAN SKILL CERTIFICATE                  │
│                                                              │
│  Skill: zotero-evidence-review                              │
│  Version: 3.9.0                                             │
│  Result: PASSED                                             │
│                                                              │
│  Author path: Copy-ready → 中文 Claim–Evidence Matrix        │
│               → Citation Insertion Sheet → Audit Appendix    │
│  Evidence rule: one claim row = one A–E level                │
│  Runtime check: Codex installed copy matches GitHub           │
│  Git commit: 9688efe                                         │
└──────────────────────────────────────────────────────────────┘
```

