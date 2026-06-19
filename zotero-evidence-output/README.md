# Zotero Evidence Output Workspace

本目录是 evidence review 的工程化工作区，用于管理 Zotero/PubMed 检索产物、稿件可用文本、claim-level evidence audit、RIS 引用包和 metadata QC。

## 1. 快速使用

1. 先打开 `PROJECT_SUMMARY.md`，确认每个 evidence package 的 `Status`、用途和主要风险。
2. 写论文时优先使用 `Ready` 或 `Caution` 报告；`Partial` 报告只能作为待补查材料。
3. 需要直接复制英文稿件文本时，优先查看各 package 的 `quick_use.md`。
4. 导入 EndNote/Zotero 时使用对应 package 的 `*_references.ris`。
5. 投稿前运行 `scripts/evidence_output_audit.py` 检查路径、RIS、状态和高风险 claim。

## 2. Status 含义

| Status | 用户含义 | 使用建议 |
|---|---|---|
| Ready | 结构完整、RIS 可用、无重大未解决证据风险。 | 可优先用于 manuscript，但仍需按目标期刊格式调整引用。 |
| Caution | 可用，但存在重要 caveat 或需要谨慎表述。 | 只能使用 hedged wording；不要把间接证据写成 direct evidence。 |
| Partial | 检索、验证或 metadata 尚未完成。 | 不应作为最终证据包；先补做 failed search 或 citation verification。 |
| Superseded | 已被更新、更完整报告替代。 | 仅保留历史记录，不建议继续引用。 |
| Unknown | 尚未完成状态评估。 | 使用前必须先审查。 |

## 3. 推荐目录规范

新 evidence package 建议逐步使用以下结构：

```text
zotero-evidence-output/
  PROJECT_SUMMARY.md
  REPORT_TEMPLATE.md
  evidence_claims_master.tsv
  reference_qc_master.tsv

  {brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/
    quick_use.md
    full_evidence_review.md
    references.ris
    reference_qc.tsv
    claims.tsv
    search_log.json
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
- 所有路径必须是相对路径，不要写入 `/Users/...` 等本机路径。

## 5. RIS 使用规则

- RIS 文件必须是 plain RIS records，不能混入 Markdown 标题、代码围栏或解释文字。
- 有 PMID 时优先使用 PubMed-standardized metadata。
- Zotero duplicate/replaced records 应从最终 RIS 中排除。
- PubMed-only 但重要的记录建议导入 Zotero 后再进入最终 manuscript reference manager。

## 6. 维护文件

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
python3 scripts/evidence_output_audit.py --input zotero-evidence-output
python3 scripts/evidence_output_audit.py --help
```

默认审计脚本只生成 draft 输出和检查报告，不会改写原始 evidence review。
