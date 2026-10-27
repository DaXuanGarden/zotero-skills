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

## 第二轮回炉：用户反馈驱动的修正

### 新验料结论

用户实际使用后给出的两个问题都成立：`My Groups` 下面重复出现段落组，说明 group-set 写入没有把“章节总组”作为唯一可见入口；Introduction 的编号段落规则被错误地泛化到 Discussion 和 Methods，说明 assignment schema 缺少章节专属的命名约束。另一个容易静默失败的事实是 EndNote AppleScript 可能只更新 `.Data/sdb/sdb.eni`，而 `.enl` 仍是旧副本；只看 EndNote 界面或只看一次导入报告都不够。

### 本轮只刨三面

1. **分组面**：adapter 只 upsert `Introduction`、`Discussion`、`Methods` 等章节 set，并把段落/方法模块作为子组；不创建新的 `My Groups`，并在写入后从既有 My Groups 成员表移除本次 bridge 生成的子组 ID。审计新增 `my_groups_leaks` 检查。
2. **命名面**：Introduction 允许 `Paragraph 1` 自动规范化为 `Introduction-01`；Discussion 和 Methods 必须使用带章节前缀的命名 ID（例如 `Discussion-Observational-evidence`、`Methods-Overview`），通用 `Paragraph-01` 会在严格模式下拒绝。正常 `--apply` 遇到未解析或未分配记录会停下。
3. **交付面**：新增 `endnote_sync.py`，明确执行“AppleScript 写 cache → 关闭 EndNote → 备份 → cache-to-main → 重新打开 → audit”的完整闭环；审计同时检查主库和 cache 记录数、期望的 section/paragraph 组以及 My Groups 泄漏。

### 第二轮验证

通过：

```text
python3 zotero-endnote-bridge/tests/test_bridge.py
python3 zotero-endnote-bridge/scripts/endnote_bridge.py --self-test
python3 zotero-endnote-bridge/scripts/endnote_audit.py --self-test
python3 zotero-endnote-bridge/scripts/endnote_metadata.py --self-test
python3 zotero-endnote-bridge/scripts/endnote_sync.py --self-test
python3 scripts/validate-endnote-bridge.py
```

真实项目 dry-run 仍为 88 条输入 → 77 条 canonical records、3 个显式 section/paragraph groups、11 条重复折叠、0 条 assignment 警告。只用引言的已标注 RIS 运行推断回放时，18 条记录被分到 `Introduction-01/02/03`，并把“推断而非 assignment”写入 warnings；这证明不会把缺少 Discussion/Methods 专属 assignment 的输入伪装成完整层级。真实 `.enl` 库本轮仍未修改。

### 质量评分更新（实测）

| 维度 | 上轮 | 本轮 | 证据 |
|---|---:|---:|---|
| 分组表达 | 4/5 | 5/5 | section set upsert、My Groups 泄漏检查、真实 manifest dry-run |
| 失败模式编码 | 4/5 | 5/5 | strict taxonomy、未分配 apply 阻断、cache 不一致报错 |
| 检查点设计 | 4/5 | 5/5 | metadata → sync → reopen → audit 固定顺序 |
| 实测表现 | 4/5 | 4/5 | fixture + 真实 RIS dry-run；未对真实库重复写入 |
| 总分 | 约 82/100 | 约 90/100 | 本轮改动均有回归测试；私有 EndNote schema 仍限制满分 |

### 回炉观察清单

- 继续观察 EndNote 2025/2026 是否改变 `misc(17,*)`、`misc(18,0)` 或 `groups` 的私有结构；schema 不匹配时必须回退到 RIS package。
- 每次 metadata refresh 后保留 `metadata-refresh.json`、`cache-sync.json` 和 `endnote-audit.json` 三份报告；缺任何一份都不标记为完成。
- 下一轮可以补充一个真实副本上的 macOS smoke test，但不把用户主库纳入 CI，也不在公共仓库保存真实文献或私人路径。
