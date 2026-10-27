# Skill 打磨报告（2026-10-27）

## 1. 验料结论

这组 Skill 仍然值得维护。真实痛点已经从“能不能检索/能不能润色”收敛为两个可测问题：预期文献找不到时，失败类型和救援策略不够明确；英文稿件改得流畅后，仍可能出现翻译腔、章节功能错位或证据边界漂移。

结论：好料，继续打磨；优先把失败模式和验收门写进可执行协议。

## 2. 访行记录

| 对标 | 链接 | 可学手艺 | 本仓库的取舍 |
|---|---|---|---|
| scholar-support | <https://github.com/mcmespinaa/scholar-support> | 首屏给出下一步和引用审计入口 | 保留 Zotero/PubMed 证据边界和 RIS 交接 |
| AI Citation Auditor | <https://github.com/SahPet/ai-citation-auditor> | 用表格呈现 citation audit 和局部支持 | 增加 claim-level source layer 与 A–E level |
| research-paper-lifecycle-skills | <https://github.com/ShaishavMaisuria/research-paper-lifecycle-skills> | 把研究任务拆成阶段 | 保留五个互补入口，不把所有任务合成一个黑箱 |
| claude-academic-workflow | <https://github.com/ericluo04/claude-academic-workflow> | 用小型专用 Skill 分担检索、写作和审计 | 明确把专用叶子编辑器列入 manuscript-thinking 路由 |

## 3. 过尺结果

| 维度 | 评分 | 证据 | 本轮重点 |
|---|---:|---|---|
| Frontmatter 与触发条件 | 9/10 | evidence 4.0.0、manuscript-thinking 0.7.0，依赖和路由清楚 | 新增检索救援和专用编辑器路由 |
| 工作流清晰度 | 9/10 | retrieval rescue、五道 polish gate、README 速查 | 将失败分类和验收顺序显式化 |
| 失败模式编码 | 9/10 | `tool_unavailable/query_error/zero_hits/metadata_unusable/support_gap` | 区分“没搜到”和“没跑通” |
| 检查点设计 | 9/10 | `POST_WRITE_AUDIT` + quality-gate fixture | 阻止过度因果、数字漂移和引用归属变化 |
| 可执行具体性 | 9/10 | DOI/PMID/题名/作者年份 ladder、anchors_preserved、manual_next_query | 为预期文献缺失提供可复制下一步 |
| 实测表现 | 8/10 | 全部本地 validator、bridge self-test 和 smoke prompt 通过 | MCP 活体检索仍需在当前会话单独运行 |
| **总分** | **88/100** | 静态门与回归夹具通过 | 下一轮收集真实失败包和润色前后样例 |

## 4. 本轮落地

### 检索可靠性

- 新增 `zotero-evidence-review/references/retrieval-rescue-protocol.md`。
- 固化 DOI → PMID → Zotero key → exact title → normalized title → author/year + distinctive title tokens 的定位阶梯。
- 要求逐级放宽时保留 population/object 和 outcome 锚点，禁止 gene-only、method-only 或 author-only 结果直接进入证据集。
- Recall Audit 新增 `failure_class`、`rescue_ladder_used`、`anchors_preserved`、`rescue_status` 和 `manual_next_query`。
- `no_direct_match` 与 `blocked` 分开，避免把工具失败误报为“没有文献”。

### 润色质量

- 新增 `zotero-manuscript-thinking/references/polish-quality-gate.md`。
- 明确按章节把最终措辞交给 `academic-introduction-polisher`、`academic-discussion-polisher`、`medical-english-precision-editor`、`writing-core`、`academic-reference-matcher` 或 `academic-ref-check`。
- 固化 meaning、section logic、field-native、language precision、evidence-boundary 五道门。
- 新增 `scripts/validate-polish-quality-gate.py` 和正/反 fixture，确保过度主张会被拒绝。
- README 增加失败救援和润色路由的使用说明，并更新版本表。

## 5. 验证结果

```text
python3 scripts/check-all.py --output-warnings skip --smoke-prompts check
python3 scripts/check-installed-skills.py --target codex --mode fail
git diff --check
```

验证要求：静态检查通过；当前会话未声称完成 Zotero/PubMed 活体检索。真实 EndNote `.enl`、`.Data` 和未跟踪历史输出目录未修改。

## 6. 回炉清单

1. 用下一次真实“预期文献缺失”任务回放 rescue ladder，记录每一级新增的直接候选和误召回率。
2. 收集 Introduction、Discussion、Methods 各一段润色前后样例，检查 `POST_WRITE_AUDIT` 是否能抓到翻译腔、术语漂移和 citation ownership 改变。
3. 将高频失败案例加入脱敏 fixture；不把用户私人库、EndNote 路径或真实凭据提交到仓库。

## 7. 出师证书

```text
┌──────────────────────────────────────────────────────────────┐
│  LUBAN SKILL CERTIFICATE                                    │
│  Zotero evidence review 4.0.0 · manuscript thinking 0.7.0   │
│  Retrieval rescue: PASS · Polish quality gate: PASS          │
│  Static quality gates: PASS                                  │
│  MCP live retrieval: not claimed in this audit               │
└──────────────────────────────────────────────────────────────┘
```
