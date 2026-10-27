# Luban polish report: `zotero-endnote-bridge`

## 验料与问题定义

本次打磨基于现有 `zotero-evidence-review` 的 EndNote-compatible RIS/assignment 输出、项目中已验证的 macOS EndNote 2025 处理脚本，以及同类 GitHub 项目的只读解析、持续导出和去重思路。现有流程能够生成 RIS 和分组信息，但不能安全地把这些信息交接到一个实际的 `.enl` 库：层级只存在于关键词和 manifest，路径写死，元数据刷新与导入分散，写入前后的审计也没有公共的可复用入口。

## 生态位与方案比较

| 方案 | 优点 | 缺口 | 决策 |
|---|---|---|---|
| 继续扩展 `zotero-evidence-review` | 入口少 | 检索、证据判断和 EndNote 私有库写入耦合；安装和测试边界不清 | 不采用 |
| 复用现有 `endnote-workflow` | 有 EndNote 术语和 Word 流程 | 目标是 Windows 临时引用，明确不支持 macOS 库写回 | 仅作为参考 |
| 新建独立 `zotero-endnote-bridge` | 职责清晰，可单独安装；RIS/assignment 边界稳定；可把私有 SQLite 适配器隔离 | 需要记录 macOS 版本差异和备份策略 | 采用 |

同行项目检查覆盖了 EndNote `.enl` 只读解析、Zotero 自动 RIS/EndNote XML 导出、Windows 端到端采集、DOCX 字段审计和通用文献管理器的批量导入。它们没有提供可直接安全复用的 macOS EndNote 分组写回实现，因此本 skill 将这些项目的可审计、可回滚和持续导出模式转化为独立的桥接层。

## 过尺评分

| 维度 | 基线 | 当前实现 |
|---|---:|---:|
| 可复现性 | 2/5 | 4/5：输入 RIS、assignment、源文件 hash、manifest 和报告均落盘 |
| 分组表达 | 2/5 | 4/5：`Section/Paragraph` 两级结构，重复归属可保留，RIS 无法表达的嵌套层级写入 manifest/SQLite adapter |
| 安全性 | 1/5 | 4/5：默认 dry-run；显式 `--apply --apply-sqlite`；schema 检查；EndNote 运行检查；`.enl`+`.Data` 备份 |
| 元数据质量 | 2/5 | 4/5：PubMed/Crossref 刷新计划、ASCII-safe AppleScript 编译、审计报告和未解析列表 |
| 可移植性 | 2/5 | 4/5：package/audit 纯 Python；macOS 私有库写入明确隔离并停止在不支持的 schema |
| 可维护性 | 2/5 | 4/5：独立 skill、安装器入口、夹具、自测和文档 |

## 实际交付

- 新增 `zotero-endnote-bridge/SKILL.md`、README、assignment schema、macOS API、备份和故障排查文档。
- 新增 `scripts/endnote_bridge.py`：RIS 规范化、按 PMID/DOI/题名-作者-年份去重、assignment 解析、`Introduction/Methods/Discussion` 分组、master/per-group RIS、manifest 和 group map；同题名但已有不同 DOI/PMID 的论文会保留为独立记录；可选 macOS SQLite adapter。
- 新增 `scripts/endnote_metadata.py`：PubMed/Crossref 元数据计划、EndNote AppleScript 生成、`osacompile` 编译和可选写回；默认只填充空字段，`--overwrite` 才覆盖。
- 新增 `scripts/endnote_audit.py`：库 schema、活动记录、必填字段、重复 DOI/PMID、组和源 RIS 覆盖审计。
- 新增纯 RIS fixture 和 Python 测试；覆盖 DOI 重复合并、段落归属、master RIS、manifest 和无私人路径输出。
- 更新 `scripts/install-skill.sh` 和仓库 README，支持单独安装或 `all-skills`。

## 验证记录

通过：

```text
python3 -m py_compile zotero-endnote-bridge/scripts/*.py zotero-endnote-bridge/tests/test_bridge.py
python3 zotero-endnote-bridge/scripts/endnote_bridge.py --self-test
python3 zotero-endnote-bridge/scripts/endnote_audit.py --self-test
python3 zotero-endnote-bridge/scripts/endnote_metadata.py --self-test
python3 zotero-endnote-bridge/tests/test_bridge.py
python3 scripts/validate-skill.py
python3 scripts/check-all.py --output-warnings warn
```

用当前项目的引言、方法和讨论 RIS 做了只读 dry-run：88 条输入记录合并为 77 条 canonical records，生成 3 个 section/paragraph groups，11 条重复被折叠，无 assignment 警告。真实 `.enl` 库没有在本次公共仓库验证中写入；已有项目库的写入、缓存同步和 76 条记录审计结果保留在本地项目资产中，不提交到仓库。

## 回炉清单与边界

1. EndNote 私有 schema 可能随版本变化；遇到 schema 不匹配时保留 RIS package，改用 EndNote 原生导入。
2. RIS 不能携带嵌套 group set；原生 RIS 导入后需要用 manifest 建组，或在确认 macOS 版本兼容后显式启用 adapter。
3. PubMed/Crossref 服务不可用时，metadata refresh 会保留失败清单，不以网络失败伪装为成功。
4. 真实库 smoke test 应在用户自己的备份副本上运行，并在重新打开 EndNote 后再次执行 audit。

## 出师证书

本次改动已在 feature branch `feat/zotero-endnote-bridge` 完成。它把证据检索、EndNote 交接、元数据刷新和最终审计分成可验证的阶段，默认不会修改用户库；真正写入需要用户明确选择 macOS 私有库 adapter。下一步只需检查 branch diff 并合并到默认分支。
