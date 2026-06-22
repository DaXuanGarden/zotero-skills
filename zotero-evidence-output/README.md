# Zotero Evidence Output Workspace

本目录是 evidence review 的工程化工作区，用于管理 Zotero/PubMed 检索产物、稿件可用文本、claim-level evidence audit、Citation Support Ledger、RIS 引用包和 metadata QC。

## 1. 快速使用

1. 先打开 `PROJECT_SUMMARY.md`，确认每个 evidence package 的 `Status`、用途和主要风险。
2. 写论文时优先使用 `Ready` 或 `Caution` 报告；`Partial` 报告只能作为待补查材料。
3. 需要直接复制英文稿件文本时，优先查看各 package 的 `quick_use.md`（如存在）；新默认报告中也应优先使用 `Copy-ready Manuscript Text`，并同步检查 `Annotated Recommended Text`。
4. 在使用推荐 citation 或导入 RIS 前，必须检查同一 Markdown report 中的 **Citation Support Ledger**：确认每条推荐引用都有 claim/sentence、inspection route、evidence location、support verdict 和 RIS action。
5. 导入 EndNote/Zotero 时使用对应 package 的 `*_references.ris`，但只应导入 ledger / Metadata QC 允许 Include 的记录。
6. 投稿前运行 `scripts/check-all.py`（默认严格失败），或分别运行 `scripts/evidence_output_audit.py`、`scripts/pubmed_output_audit.py` 与 `scripts/ris_lint.py`，检查路径、RIS、状态、高风险 claim、编号引用修复表和 ledger 结构；历史旧包较多时可用 `scripts/check-all.py --output-warnings warn` 先查看 warnings。

## 2. Status 含义

| Status | 用户含义 | 使用建议 |
|---|---|---|
| Ready | 结构完整、RIS 可用、无重大未解决证据风险。 | 可优先用于 manuscript，但仍需按目标期刊格式调整引用。 |
| Caution | 可用，但存在重要 caveat 或需要谨慎表述。 | 只能使用 hedged wording；不要把间接证据写成 direct evidence。 |
| Partial | 检索、验证或 metadata 尚未完成。 | 不应作为最终证据包；先补做 failed search 或 citation verification。 |
| Superseded | 已被更新、更完整报告替代。 | 仅保留历史记录，不建议继续引用。 |
| Unknown | 尚未完成状态评估。 | 使用前必须先审查。 |

## 3. 默认输出与可选工程化结构

当前 `zotero-evidence-review` skill 的默认 evidence package 只生成两个文件：

```text
zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_evidence_review.md
zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_references.ris
```

除非用户明确要求，不默认生成 `quick_use.md`、TSV、JSON、BibTeX、EndNote XML 或额外日志文件。Markdown report 是人工可读的 evidence workspace；RIS 是 EndNote/Zotero 导入文件。

旧 package 或人工整理后的项目级工作区可能包含以下扩展结构；这些文件是维护/汇总用途，不是新运行的默认交付物：

```text
zotero-evidence-output/
  PROJECT_SUMMARY.md
  REPORT_TEMPLATE.md
  evidence_claims_master.tsv
  reference_qc_master.tsv

  {brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/
    {brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_evidence_review.md
    {brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_references.ris
    quick_use.md                 # optional
    reference_qc.tsv             # optional
    claims.tsv                   # optional
    search_log.json              # optional
```

当前旧 package 仍保留原始文件名，例如：

```text
sedentary_behavior_pcos_gwas_2026-06-19_021111/sedentary_behavior_pcos_gwas_2026-06-19_021111_evidence_review.md
sedentary_behavior_pcos_gwas_2026-06-19_021111/sedentary_behavior_pcos_gwas_2026-06-19_021111_references.ris
```

不要为了美观批量重命名旧目录；应先在 `PROJECT_SUMMARY.md` 建立用途和 canonical mapping。

## 4. 写作安全规则

- 如果证据不是 exact claim direct support，必须 hedge。
- Current-study finding 和 external evidence 必须分开写。
- PubMed failed query 不能隐藏，必须标记为 `Partial` 或 `Caution`。
- 不要用 Zotero/PubMed 文献为本研究的 MAGMA、TWAS、SMR、colocalization 或 enrichment 结果背书。
- 不要把 biological plausibility 写成 established mechanism。
- Citation Support Ledger 中 `not inspected`、`contradicts`、`not addressed` 的行必须先排除或复核，不能直接进入 manuscript 引文或 RIS。
- Citation Support Ledger 中 `background only` 的行只能支持背景/语境表述；若 manuscript 句子写成 direct support，应先改写或换引文。
- PubMed 搜索 snippet 只能作为发现线索；PubMed-only 引用应有 PMID Inspection Ledger 的 completed inspection 记录。
- 所有路径必须是相对路径，不要写入 `/Users/...` 等本机路径。

## 5. RIS 使用规则

- RIS 文件必须是 plain RIS records，不能混入 Markdown 标题、代码围栏或解释文字。
- 有 PMID 时优先使用 PubMed-standardized metadata；RIS 中 `PM` 可作为 PMID 字段，但不能替代作者、标题、年份等关键 metadata。
- Zotero duplicate/replaced records 应从最终 RIS 中排除。
- Citation Support Ledger 的 `RIS action` 是 RIS 使用前的主审计字段：`not inspected`、`contradicts`、`not addressed` 默认不能 Include；`background only` 默认 Optional，只有当稿件文字明确作为背景/语境时才可 Include。
- PubMed-only RIS 记录必须对应 PMID Inspection Ledger 中 `Inspection status = completed`、无未解决 retraction/metadata warning、且 `RIS action = include` 的行。
- PubMed-only 但重要的记录建议导入 Zotero 后再进入最终 manuscript reference manager。

## 6. 维护文件

`Citation Support Ledger` 默认嵌入在每个 `*_evidence_review.md` 的 Citation Placement 部分，不是单独的默认文件。它把 copy-ready text、annotated text、Citation Placement、Reference Table、Reference Canonicalization Gate、Metadata QC 和 RIS action 连接起来，便于追踪每个 claim/sentence 的推荐引用是否经过检查、证据位置在哪里、是否允许进入 RIS。

| File | Purpose |
|---|---|
| `PROJECT_SUMMARY.md` | 项目级 dashboard 和推荐使用顺序。 |
| `_inventory_initial.tsv` | 初始 evidence package inventory。 |
| `REPORT_TEMPLATE.md` | 新 evidence review 的固定 Markdown 模板。 |
| `evidence_claims_master.tsv` | 项目级 claim registry。 |
| `reference_qc_master.tsv` | 项目级 canonical reference / metadata QC registry。 |
| `ENGINEERING_DEVELOPMENT_PLAN.md` | 工程化开发计划和后续路线图。 |

## 7. 审计命令

```bash
# 一键只读质量门禁：skill validator + output audit + RIS lint；默认 strict，warnings 会失败
python3 scripts/check-all.py

# 历史旧包噪音较多时：仍运行 output audit/RIS lint，但 warnings 只打印、不让 check-all 失败
python3 scripts/check-all.py --output-warnings warn

# 只跑 skill validators，跳过 output package audit/lint
python3 scripts/check-all.py --output-warnings skip

# 仍严格检查新包，但抑制 cutoff 之前历史 output package/RIS warnings
python3 scripts/check-all.py --ignore-output-warnings-before 2026-06-20

# 只审计 evidence package；默认只读，不写 draft 文件；会检查 Citation Support Ledger 结构和 unsafe RIS Include
python3 scripts/evidence_output_audit.py --input zotero-evidence-output
python3 scripts/evidence_output_audit.py --input zotero-evidence-output --fail-on-warnings
python3 scripts/evidence_output_audit.py --input zotero-evidence-output --fail-on-warnings --ignore-before 2026-06-20

# 如果存在 pubmed-literature-output，check-all.py 会条件性运行 PubMed output audit
# 也可以单独审计 PubMed literature package 的 PMID Inspection Ledger 与 RIS PMID 对应关系
python3 scripts/pubmed_output_audit.py --input pubmed-literature-output
python3 scripts/pubmed_output_audit.py --input pubmed-literature-output --fail-on-warnings
python3 scripts/pubmed_output_audit.py --input pubmed-literature-output --fail-on-warnings --ignore-before 2026-06-20

# 只检查 RIS 是否混入 Markdown、占位符或缺少关键字段
python3 scripts/ris_lint.py zotero-evidence-output --fail-on-warnings
python3 scripts/ris_lint.py zotero-evidence-output --fail-on-warnings --ignore-before 2026-06-20

# 查看可选写入 draft 汇总/TSV 的参数
python3 scripts/evidence_output_audit.py --help
```

默认审计脚本是 read-only：不会改写原始 evidence review，也不会自动生成 `PROJECT_SUMMARY.draft.md`、`evidence_claims_master.draft.tsv` 或 `reference_qc_master.draft.tsv`。只有显式传入 `--write-summary`、`--write-claims` 或 `--write-reference-qc` 时才会创建 draft 文件。`check-all.py` 默认是 strict；`--output-warnings warn` 只降低 output warnings 的退出码，不表示 warnings 已解决；`--ignore-before` 只抑制历史 warning，RIS error 仍会失败。`check-all.py` 会在 `zotero-evidence-output` 存在时运行 Zotero evidence output audit，并在 `pubmed-literature-output` 存在时条件性运行 PubMed output audit。

这些脚本是工程化质量门禁，不能替代人工/工具级证据核查：它们不会连接 Zotero、不会执行 PubMed，也不会证明某篇文献真实支持某个 manuscript claim。Citation Support Ledger 与 PMID Inspection Ledger 是可审计链和输出结构要求，不是语义真值证明。
