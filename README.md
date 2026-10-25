# 📚 Zotero Skills

> 面向 Codex / OpenCode / ZCode 的 Zotero 文献证据审查技能：让 AI 助手在你的 Zotero 文献库中检索、分析、核实引用，并给出可追溯的写作建议。

![Codex](https://img.shields.io/badge/Codex-Skill-412991)
![OpenCode](https://img.shields.io/badge/OpenCode-MCP-0175C2)
![ZCode](https://img.shields.io/badge/ZCode-Skill-6f42c1)
![Zotero MCP](https://img.shields.io/badge/Zotero-MCP-CC2936)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 0. 最短路径：按场景直接开始

如果你已经安装好 skill，并且当前 Codex / ZCode / OpenCode 会话能看到 Zotero MCP（可选：PubMed MCP），最省事的用法是：**复制下面与你场景最接近的提示词，把主题、段落或参考文献替换成自己的内容即可。**

默认行为已经调整为“检索也导出”：普通文献检索、目标文献检索、段落补引用/润色、PubMed 主题检索都会默认生成 Markdown 报告 + EndNote-compatible RIS。只想在聊天里快速看结果时，请在提示词开头明确写 `只在聊天输出，不要生成文件`。

写作任务建议按一条可追踪的流水线推进：

```text
收集素材 → 阅读并抽取 peer patterns → 建立 evidence/style/argument profiles
→ 先做全文意义与章节逻辑 → 再做领域语言校准和局部改写 → 回查主张、数字、引用与 Methods–Results 对齐
```

`zotero-literature-learning` 负责前半段，`zotero-manuscript-thinking` 负责整体诊断与修订顺序，`zotero-evidence-review` 负责具体 claim 的支持、核实和 RIS。三者共享 handoff，不各自重复建立文献出口。

段落证据工作现在还会产出一张逐句矩阵：每句话都有稳定的 `sentence_id`，并沿着 `sentence_id → claim_id → citation → RIS action` 回溯。这样可以区分“需要外部引用”“本研究结果”“常识”“解释性桥接”和“证据缺口”，也能发现一篇文献被误用来覆盖整段的情况。矩阵旁边的 `CITATION_COVERAGE_SUMMARY` 会给出覆盖率、未映射主张和孤立 RIS 候选；覆盖链不完整时，报告不会标记为 `Ready`。段落请求还默认提供 `Copy-ready Manuscript Text`、`Citation Insertion Sheet`（插入锚点、可复制作者–年份引文、Zotero/EndNote 搜索词、PMID/DOI）和 `Diff / Change Log`；明确说“只找引文/保留原文措辞”时才跳过润色层。

最简调用方式就是只给段落：

```text
/zotero-evidence-review 帮我找到这个段落每句话合适的引文，并生成可导入 EndNote 的 RIS：

{粘贴段落}
```

不需要手动拆句、写检索词或提供 claim ID。Skill 会默认先查 Zotero，再在 PubMed MCP 可见时扩展检索；它会逐条检查证据位置和支持强度，最后输出逐句引用矩阵、Markdown 报告和 Citation RIS。只想看聊天结果时，加上 `只在聊天输出，不要生成文件`。

当你希望同一句话有多个写法时，三个 Skill 共享 `WRITING_OPTIONS_CARD`：先做意义和证据门禁，再给出最多三个带有明确角度的候选，最后由作者选择。默认候选是 `Conservative`（保留原意）、`Field-native`（依据同领域语料校准）和 `Logic-forward`（重排论证顺序）。每个候选都显示 `claim_delta`、证据等级、引用集合、适用场景和风险；未选择前不会把第一版当作最终稿。

| 场景 | 推荐入口 | 复制即用提示词 | 典型产物 |
|---|---|---|---|
| 写论文时给一段草稿找证据、补引用 | `/zotero-evidence-review` | `帮我找到这个段落每句话合适的引文：...`（只粘贴段落即可） | `*_evidence_review.md`（含 Copy-ready、Citation Insertion Sheet、Diff）+ `*_references.ris` |
| 从全文角度检查语言、Methods/Results、Introduction/Discussion 和主线 | `/zotero-manuscript-thinking` | `请检查语言精确度、Methods/Results/Introduction/Discussion 逻辑和全文主线，找出 P0/P1 问题，并给出下一轮修改顺序，不要直接重写全文。` | `MANUSCRIPT_STRATEGIC_REVIEW`（结构与语言诊断；不自动生成 RIS） |
| 先从 Zotero 收集并学习同领域素材，再开始改稿 | `/zotero-literature-learning` | `先从 Zotero 找 3–5 篇同领域、同文章类型的论文，读取摘要/全文，学习 Introduction/Methods/Results 的写法，形成素材包，再交给下游 Skill。` | `MATERIALS_LEARNING_REPORT` + corpus/evidence/style/argument profiles + handoff |
| 写作卡住时学习专业表达或方法术语 | `/zotero-literature-learning` | `这句话太啰嗦；请从 Zotero 找同领域、同章节的高匹配片段，比较表达后给出 2–3 个保守版本，并核对 annotation 是否准确。` | `WRITING_BLOCK_LEARNING` + writing block card + author checks |
| 同一句话需要多个角度 | `/zotero-manuscript-thinking` 或 `/zotero-evidence-review` | `请给这句话提供 Conservative、Field-native 和 Logic-forward 三个版本，绑定各自证据、风险和适用场景，先不要替我选择。` | `WRITING_OPTIONS_CARD` + 候选比较表 + selection_status |
| 参考同领域代表性论文校准地道表达 | `/zotero-manuscript-thinking` | `请从 Zotero 选 3–5 篇同领域、同文章类型的代表性论文，比较这段 Introduction 的段落推进、术语和 claim verbs，再给保守改写；不要复制原文。` | `Domain Style Calibration` + peer-pattern 对照表 + copy-ready 文本 |
| 校准 Methods/Results 的地道写法与证据边界 | `/zotero-manuscript-thinking` | `请从 Zotero 选同领域、同研究设计的论文，检查我的 Methods 是否可复现、Results 是否按主要发现推进，并核对 Methods–Results–图表一致性；先给 Logic Map，再润色。` | `Methods Logic Map` + `Results Logic Map` + reproducibility/alignment audit |
| 已有编号引用，怀疑某些引用不支持原句 | `/zotero-evidence-review` | `帮我检查并更新下面这段已有编号引用，逐条判断引用是否支持原句，修复不支持的引用，并生成最终 RIS：...` | 引用支持/不支持表、改写段落、最终 RIS |
| 在 Zotero 库里找文献并导出 | `/zotero-evidence-review` | `搜 Zotero 库中关于 {topic} 的论文，列出最相关的 10 篇，并说明每篇适合支持什么主张。` | `*_literature_search.md` + Search RIS；显式 chat-only 时只聊天 |
| 目标文献检索与文献清单导出 | `/zotero-evidence-review` | `哪些文献使用了大脑相关 GWAS 数据？请拆解检索主题，分类 Core/Strong Related/Noise，并导出 MD 和 RIS。` | `*_literature_search.md` + Search RIS |
| Zotero 证据不够，需要补 PubMed | `/zotero-evidence-review` | `先检索 Zotero；如果证据不足，在 PubMed MCP 可用时扩展检索，并合并去重后生成 Evidence Package：...` | Zotero + PubMed 合并证据报告、RIS |
| 只做 PubMed 检索，不依赖 Zotero | `/pubmed-literature-search` | `检索近 5 年 {topic} 的 PubMed 文献，检查 PMID 元数据，找 related reviews，并导出 Markdown 报告和 RIS。` | PubMed-only report + RIS |
| 核实一篇文献是否真的支持某句话 | `/zotero-evidence-review` | `请核实这篇文献是否支持以下主张：claim = ...；文献 = DOI/PMID/Zotero key/...；优先读取全文/PDF。` | fully/partially/contradicted/not addressed 判断 |
| 投稿前检查库和输出质量 | `/zotero-evidence-review` + 本地脚本 | `做一次 Zotero library health check，只读检查，不要修改条目。` 然后本地运行 `python3 scripts/check-all.py` | 索引/PDF/重复/缺元数据状态、输出门禁 |

完整工作流可以记成一句话：

```text
草稿或问题 → Zotero 本地检索 → claim 拆解/检索分类 → PubMed 可见时自动扩展 → 引文放置与改写或文献清单分类 → Citation/PMID Ledger → Markdown report + EndNote RIS → EndNote/Word 中重排编号
```

最常用的端到端提示词：

```text
/zotero-evidence-review 帮我给下面这段论文草稿找证据并补引用，使用完整工作流：
1. 先检索 Zotero 本地库；
2. 如果 PubMed MCP 可用，再做 PubMed 扩展并去重；
3. 每个推荐引用都要说明支持哪个 claim、证据位置和支持强度；
4. 生成 Markdown evidence report 和可导入 EndNote 的 RIS；
5. 如果某个工具不可用，请明确标注，不要假装已检索。

{粘贴你的段落}
```

如果只想看结果、不想写文件，在提示词开头加一句：

```text
只在聊天输出，不要生成文件：
```

如果已经通过 `target_literature_search` 完成检索、分类和元数据检查，并整理成候选 JSON，可以用 Phase 3 writer 直接生成标准专题检索包：

```bash
python3 scripts/write_literature_search_package.py \
  --input scripts/fixtures/literature_search_package_sample.json \
  --output-root /tmp/zotero-lit-test \
  --slug brain_gwas \
  --timestamp 2026-07-07_120000
```

这个脚本只负责把已检查候选写成 `*_literature_search.md` 和 Search RIS；它不会调用 Zotero 或 PubMed，也不会把 `Exclude` / `Verify` 条目写入 RIS。需要把 `Optional` 条目也写入 RIS 时，显式加 `--include-optional`。

如果已经有确认过的 canonical RIS，并且希望按论文段落建立 EndNote 归属，可准备一个 assignments JSON，再运行：

```bash
python3 scripts/write_endnote_collection_package.py \
  --ris path/to/canonical_references.ris \
  --assignments path/to/manuscript_assignments.json \
  --output-root zotero-evidence-output
```

它会生成一个去重总 RIS、`endnote-import/Introduction/Introduction-01.ris` 等选择性分组 RIS、JSON manifest 和 Markdown 映射表。总 RIS 只导入一次；段落归属写入 RIS `KW` 字段，避免把同一篇文献重复导入 EndNote。

---

## 1. 项目概览

本仓库提供四个互补 skill：`zotero-evidence-review` 是核心 Zotero 本地证据审查工作流；`zotero-literature-learning` 负责从 Zotero 检索、筛选、阅读和抽取可迁移素材；`zotero-manuscript-thinking` 是在局部修改后抬头检查整篇论文的论证与修订策略子 Skill；`pubmed-literature-search` 是独立 PubMed MCP 文献检索工作流。证据审查 Skill 通过 Zotero MCP 连接本地 Zotero 文献库，支持从“找文献”到完整的 **Paragraph Citation Package Workflow**（段落 → 主张拆解 → Zotero 本地检索 → PubMed 可见时自动扩展 → 引文放置 → Markdown 证据报告 + EndNote RIS）再到“逐条核实引用是否真的支持主张”的证据审查工作流；manuscript-thinking 在需要时重建 paper contract、argument spine、claim–evidence–section map，并把 P0/P1 问题交给证据、审计、修订或语言模块；PubMed skill 可直接调用 PubMed MCP 进行主题检索、PMID 元数据检查、related/review discovery、OA 全文可用性检查，并默认导出 Markdown + RIS，除非显式 chat-only。

推荐使用路径：

- 需要基于本地 Zotero 库找证据、补引用、核实引文时，用 `zotero-evidence-review`。
- 需要先收集、筛选、阅读和学习 Zotero 中的同领域论文，再进入写作时，用 `zotero-literature-learning`。
- 需要直接检索 PubMed、检查 PMID、找 related/review 文献或导出 PubMed-only RIS 时，用 `pubmed-literature-search`。
- 如果只想聊天查看结果，可明确说 `只在聊天输出` 或 `不要生成文件`；否则检索、补引用和润色都会默认生成相应报告与 RIS。

| 项目 | 当前状态 |
|---|---|
| Skill | `zotero-evidence-review` / `zotero-literature-learning` / `zotero-manuscript-thinking` / `pubmed-literature-search` |
| 当前版本 | Zotero evidence `3.6.0`；literature learning `0.4.0`；manuscript-thinking `0.6.0`；PubMed `1.0.0` |
| 兼容性 | Codex / OpenCode / ZCode |
| 主要依赖 | Zotero 7+、zotero-mcp、Python 3.10+；PubMed 检索 skill 需要 PubMed MCP（推荐 PancrePal） |
| 安装目标 | Codex 全局、ZCode 全局、OpenCode 全局、项目级 `.opencode/skills` |
| 默认安全策略 | 健康检查只读；删除、批量修改、合并重复项等操作必须先确认 |

---

## 2. 核心能力

| 能力 | 说明 |
|---|---|
| **Intent Detection** | 根据用户输入自动判断是文献检索、段落证据分析、引用核实，还是库健康检查。 |
| **Library Health Check** | 只读检查语义索引、PDF 覆盖、重复条目、缺失摘要等状态；不可用项目明确标记为 `⚠️`。 |
| **Semantic + Structured Search** | 优先语义搜索概念相近文献，并结合标题、作者、关键词、DOI、PMID、年份等结构化检索兜底。 |
| **Collection and Tag Search** | 支持按 Zotero collection、tag、分类范围缩小检索。 |
| **Target Literature Search** | 面向无稿件段落的专题文献检索、目标文献筛选、Core/Strong Related/Verify/Noise 分类、MD/RIS 文献清单导出。 |
| **Paragraph Citation Package Workflow** | 段落补引用默认是一个完整工作流：claim extraction → Zotero semantic + structured lanes → PubMed broad/design lanes → recall audit → evidence matrix / citation placement / diff paragraph → canonical metadata → Markdown report + EndNote RIS。 |
| **Recall-first retrieval** | 不因找到一篇支持文献就停止；记录多组检索式、候选池、去重、覆盖缺口和饱和停止理由，再挑选最合适的引用。 |
| **Zotero + PubMed Dual-MCP Workflow** | Zotero MCP 负责本地库、PDF/笔记/collection/语义检索；PubMed MCP 负责独立的广召回、MeSH/题录检索、设计/方法扩展、related discovery、PMID 元数据与标准化。 |
| **Citation Verification Protocol** | 针对具体文献和具体主张读取元数据与全文，判断 fully supported / partially supported / contradicted / not addressed。 |
| **Chinese Academic Writing Rules** | 面向中文学术写作，保留原意、避免虚构引用，输出可追踪的润色与补引建议。 |
| **External Source Fallback** | Zotero 库证据不足时，可在外部 MCP 工具已配置的前提下辅助扩展；未配置时只给出可复制检索式。 |
| **Evidence Package Export** | 作为 Paragraph Citation Package Workflow 的导出阶段，生成 Markdown 证据报告与唯一 canonical RIS，并附 `ZOTERO_IMPORT_HANDOFF` 与 `ENDNOTE_IMPORT_HANDOFF`；PubMed-only 条目不伪造 Zotero key，实际写入 Zotero/EndNote 文库均由用户明确确认。 |
| **Section-aware EndNote collection** | 用户提供章节和段落边界时，生成 `Introduction/Introduction-01`、`Discussion/Discussion-01` 等稳定归属；主 RIS 只保留一份记录并写入 section/paragraph/claim/role 关键词，同时生成分组 RIS、JSON manifest 和 Markdown 映射表。 |
| **Literature Search Package Writer** | `python3 scripts/write_literature_search_package.py` 从已检查候选 JSON/YAML 生成 `*_literature_search.md` 和 Search RIS；不调用 Zotero/PubMed。 |

### 2.1 一页式使用速查

如果你只想高效完成任务，可以按下面选择：

| 你的场景 | 直接使用的提示词 | 默认结果 | 何时加限定 |
|---|---|---|---|
| 给一段草稿找证据并补引用 | `/zotero-evidence-review 帮我给下面这段草稿找证据并补引用，生成 Evidence Package：...` | Zotero 检索 + 可用时 PubMed 扩展 + Markdown report + RIS | 如果不想生成文件，加 `只在聊天输出` |
| 已有编号引用，想检查是否支持原句 | `/zotero-evidence-review 帮我检查并更新下面这段已有编号引用，指出哪些引用不支持，并生成最终 RIS：...` | 编号引用修复表 + Citation Support Ledger + 改写建议 + RIS | 如果只想看问题，不要 RIS，加 `不要导出` |
| 在 Zotero 库里找文献 | `/zotero-evidence-review 搜 Zotero 库中关于 {topic} 的论文，列出最相关的 10 篇并说明用途。` | 默认生成 search Markdown report + Search RIS；生物医学主题在 PubMed 可见时自动扩展 | 想限制范围时加 collection / tag；纯聊天加 `只在聊天输出` |
| 想筛选某主题的目标文献清单 | `/zotero-evidence-review 哪些文献使用了 {data/method/phenotype}？请输出专题检索报告和 RIS。` | target_literature_search：Topic Decomposition + Query Expansion Plan + 分类/排除原因 + `*_literature_search.md` + Search RIS | 如果只想看聊天结果，加 `只在聊天输出，不要生成文件` |
| 直接检索 PubMed | `/pubmed-literature-search 检索近 5 年 {topic} 的 PubMed 文献，检查 PMID 元数据，并列出可引用研究。` | 默认生成 PubMed report + RIS；Zotero MCP 可见时做本地库 cross-check | 纯聊天加 `只在聊天输出，不要生成文件` |
| 核实某篇文献是否支持某个 claim | `/zotero-evidence-review 请核实这篇文献是否支持以下主张：claim = ...; 文献 = DOI/PMID/Zotero key/...` | 支持度判断、证据位置、建议措辞 | 要求全文核实时写 `优先读取 PDF/全文` |
| 写作前检查 Zotero 库状态 | `/zotero-evidence-review 做一次 Zotero library health check，只读检查，不要修改条目。` | 索引/PDF/重复/缺元数据状态 | 默认只读；破坏性操作需单独确认 |

最推荐的完整写作路径是：

```text
草稿段落 → /zotero-evidence-review 生成 Evidence Package → 阅读 Markdown report 的 Bottom Line / Copy-ready Text → 检查 Citation Support Ledger → 只导入 RIS action = Include 的 RIS → 在 Word/EndNote 中重排编号 → 投稿前运行 python3 scripts/check-all.py
```

阅读 Evidence Package 时优先看 5 个位置：

1. `Critical Warnings`：是否有不能直接使用的证据风险。
2. `Copy-ready Manuscript Text`：可复制进稿件的建议文本。
3. `Citation Support Ledger`：每个 claim/sentence 的推荐引用、证据位置、支持结论和 RIS action。
4. `Reference Table` / `Metadata Quality Control`：作者、年份、DOI、PMID、重复项和标准化来源。
5. `Export File`：实际生成的 Markdown 与 RIS 相对路径。

不要把 PubMed 搜索结果 snippet 直接当作可引用证据；PubMed-only RIS 需要 PMID Inspection Ledger 显示 completed inspection。不要把 Citation Support Ledger 当作语义真值证明；高风险 claim 仍需人工或全文复核。

---

## 3. 5 分钟快速安装

### 3.1 前置条件

请先确认：

- 已安装并打开 **Zotero 7+**。
- Zotero 中已启用本地访问：Zotero 设置 → 高级 → 允许其他应用程序访问 Zotero。
- 已安装 **Python 3.10+**。
- 已安装 Codex、OpenCode 或 ZCode。
- 已安装并配置 `zotero-mcp`（见 [第 5 节](#5-配置-zotero-mcp)），用于 `zotero-evidence-review`。
- 如果需要 PubMed 扩展、PMID 标准化、related/review discovery、OA 全文检测，另行配置 PubMed MCP（见 [PubMed Expansion](#83-pubmed-expansion) 和 [`docs/PANCREPAL_PUBMED_MCP_GUIDE.md`](./docs/PANCREPAL_PUBMED_MCP_GUIDE.md)）；独立 `pubmed-literature-search` skill 需要 PubMed MCP。

### 3.2 克隆仓库并安装到 Codex / ZCode / OpenCode

```bash
git clone https://github.com/DaXuanGarden/zotero-skills.git
cd zotero-skills

# 安装/更新全部 skill 到 Codex 全局目录，并清理旧的时间戳备份
bash scripts/install-skill.sh --skill all-skills --target codex --prune-backups

# 如果使用 ZCode 或 OpenCode，把 target 改成 zcode 或 opencode
bash scripts/install-skill.sh --skill all-skills --target zcode --prune-backups

# 验证 skill 文件结构与本地输出质量门禁
python3 scripts/validate-skill.py
python3 scripts/validate-pubmed-skill.py
python3 scripts/validate-literature-learning.py
python3 scripts/check-all.py
```

`python3 scripts/validate-skill.py` 和 `python3 scripts/validate-pubmed-skill.py` 是静态校验工具：它们检查 skill frontmatter、依赖声明、章节、输出模板、Evidence Package/RIS 约束和外部工具安全防护说明；它们不会连接 Zotero、不会执行 PubMed 检索，也不会验证真实引文是否支持稿件主张。

`python3 scripts/check-all.py` 是只读本地质量门禁，会串行运行两个 skill validator、Phase 3 literature search writer self-test，并在输出目录存在时运行 output audit 和 RIS lint。默认模式等价于严格提交前检查：`python3 scripts/evidence_output_audit.py --fail-on-warnings` 与 `python3 scripts/ris_lint.py --fail-on-warnings` 都会把 warning 作为失败；如果历史 evidence package 触发 warning，应按报告逐项判断是旧产物问题还是需要更新模板。处理旧包噪音时可显式使用 `python3 scripts/check-all.py --output-warnings warn`（打印但不因 output warnings 失败）、`python3 scripts/check-all.py --output-warnings skip`（只跑 skill validators 和 writer self-test），或 `python3 scripts/check-all.py --ignore-output-warnings-before YYYY-MM-DD`（仍严格检查新包，但抑制 cutoff 之前旧包的 warnings；RIS errors 仍会失败）。

### 3.3 功能覆盖检查矩阵

下面这些命令是仓库侧“真实可运行”的检查。它们不会替代 Zotero/PubMed MCP 的真实运行，但能确认 skill 文本、路由模板、writer、RIS 规则和 smoke prompt guardrail 没有漂移。

| 要检查的功能 | 可运行命令 | 通过代表什么 |
|---|---|---|
| Zotero evidence review skill 结构、段落证据包、target search、Search RIS / Citation RIS 规则 | `python3 scripts/validate-skill.py` | `zotero-evidence-review/SKILL.md` 的章节、模板、路由、RIS guardrail 和 Phase 3 writer handoff 符合仓库规范 |
| PubMed literature search skill 结构和 PMID inspection guardrail | `python3 scripts/validate-pubmed-skill.py` | `pubmed-literature-search/SKILL.md` 的 PubMed 检索、PMID metadata inspection、RIS 模板结构有效 |
| Phase 3 目标文献检索包 writer | `python3 scripts/write_literature_search_package.py --self-test` | fixture 能生成 `*_literature_search.md` 与 Search RIS，且 RIS 记录边界可校验 |
| 历史/新生成 RIS 文件格式 | `python3 scripts/ris_lint.py zotero-evidence-output` | 扫描 `.ris` 是否含 Markdown、缺少 `TY  -` / `ER  -`、明显占位符或常见字段问题 |
| 全仓库本地质量门 | `python3 scripts/check-all.py --output-warnings skip --smoke-prompts check` | 两个 skill validator、writer self-test、smoke prompt guardrail 全部通过 |
| MCP 配置文件形态 | `python3 scripts/mcp_config_sanity.py --client auto` | 本机 ZCode/OpenCode 配置 JSON、MCP server command 路径和关键 env 形态可读 |
| 已安装 skill 是否与仓库一致 | `python3 scripts/check-installed-skills.py --target all --mode warn` | 能发现 `~/.codex/skills`、`~/.zcode/skills`、OpenCode 全局、项目级 `.opencode/skills` 与仓库源码是否漂移 |

真正的 Zotero / PubMed 运行时能力必须在 Codex / ZCode / OpenCode 会话中用 smoke prompt 验证，因为只有当前会话的 MCP tool list 才能证明工具可调用：

```bash
python3 scripts/smoke_prompts.py --list
python3 scripts/smoke_prompts.py --prompt zotero-health
python3 scripts/smoke_prompts.py --prompt zotero-target-export-dry-run
python3 scripts/smoke_prompts.py --prompt pubmed-readiness
```

把打印出的 prompt 复制进新开的 Codex / ZCode / OpenCode 会话执行。若工具不可见或失败，正确结果应是报告 `unavailable` / `not executed`，而不是假装完成检索。

可选运行时诊断 gate 默认关闭，避免因为不同机器的本地 MCP 配置影响常规校验；需要排查 Zotero/PubMed MCP 时可显式开启：

```bash
# 只读检查 ZCode/OpenCode MCP config 形态、command 路径和关键 env；不启动 MCP、不联网
python3 scripts/check-all.py --output-warnings skip --mcp-config warn

# 检查仓库 skill 与 ~/.codex/skills、~/.zcode/skills、OpenCode skill 副本是否漂移
python3 scripts/check-all.py --output-warnings skip --installed-skills warn

# 校验或打印可复制的人工 MCP smoke-test prompts
python3 scripts/check-all.py --output-warnings skip --smoke-prompts check
python3 scripts/smoke_prompts.py
```

也可以单独运行：`python3 scripts/mcp_config_sanity.py --client auto`、`python3 scripts/check-installed-skills.py --target all --mode warn`、`python3 scripts/smoke_prompts.py --check`。

### 3.4 静态校验 vs 运行时 MCP 就绪

静态校验通过只说明 skill 文本结构正确，不等于当前 Agent IDE 会话已经能调用 Zotero / PubMed。真正执行工作流前，请按下面的只读 checklist 快速确认：

| 检查项 | 期望状态 | 不满足时的正确行为 |
|---|---|---|
| Zotero MCP 工具可见 | 当前会话能看到 Zotero search / metadata / fulltext / children 等工具 | 不声称已完成 Zotero 本地检索；先修复 MCP 配置 |
| Zotero 语义索引 / fulltext 可用 | 可读取 `zotero_get_search_database_status`，必要时能访问 PDF/fulltext | 报告索引或全文限制；不要虚构全文核查 |
| PubMed MCP 工具可见（可选） | 当前会话能看到 `pubmed_search`、`pubmed_get_details`、`pubmed_extract_info`、`pubmed_find_related` 等 PubMed/NCBI 工具 | 报告 `PubMed: ⚠️ Tool unavailable; search not executed`，并给出可复制 query |
| PubMed 已实际运行且元数据已检查 | PubMed search 有返回，候选 PMID 已用详情/抽取工具检查 | 只有此时才能写 `PubMed: Completed` 或生成 PubMed-only RIS |

换句话说：validator 是仓库侧 guardrail；MCP readiness 是当前 Codex / ZCode / OpenCode 会话侧状态。PubMed 不可见不是 Zotero 检索失败，而是可选 PubMed 扩展层未接入。

本仓库提供三个只读辅助脚本来定位“配置存在但当前会话不能稳定调用”的问题：

| 脚本 | 用途 | 是否调用 MCP/联网/改配置 |
|---|---|---|
| `python3 scripts/mcp_config_sanity.py --client auto` | 检查 `~/.zcode/v2/config.json`、`~/.zcode/cli/config.json`、`~/.config/opencode/opencode.json` 的 JSON 形态、`mcp`/`mcp.servers`/`mcpServers` 差异、command 路径、GUI PATH 风险、PubMed/Zotero 关键 env | 否 |
| `python3 scripts/check-installed-skills.py --target all --mode warn` | 比较仓库 `SKILL.md` 与 `~/.zcode/skills`、OpenCode 全局、项目级 `.opencode/skills` 中的 installed copy 是否一致 | 否 |
| `python3 scripts/smoke_prompts.py` | 打印可复制到 ZCode/OpenCode 的安全人工 smoke-test prompt，强调只读、分步调用、不可伪造结果 | 否 |

如果 `mcp_config_sanity.py` 提示 `mcpServers`，通常说明把 Claude 风格配置粘贴到了 ZCode/OpenCode 配置；如果提示 command 不是绝对路径，GUI 启动的 ZCode/OpenCode 可能拿不到 shell `PATH`。这些脚本只能检查本地文件和 prompt 文本，不能替代当前会话真实 MCP tool list；修改配置或同步 skill 后仍需完整重启客户端或开启新会话。

如果验证成功，会看到类似：

```text
✅ frontmatter parsed; version 2.8.0
✅ markdown code fences balanced
✅ required workflow headings present
✅ section numbering is consistent
✅ evidence package export requirements present
✅ RIS export requirements present
✅ appendix template definitions present
✅ Evidence Review report template sections present
✅ external-tool availability guards present

All validations passed.
```

### 3.5 安装后第一次完整试跑

安装、MCP 配置和静态校验完成后，建议先用一个短段落做端到端试跑，确认当前 Agent 会话能看到 Zotero/PubMed 工具，并能正确生成 evidence package：

```text
/zotero-evidence-review 用完整工作流帮我给下面这段草稿找证据并补引用，生成 Markdown evidence report 和 EndNote RIS；如果 PubMed 工具不可用，请只报告 query，不要声称已完成 PubMed 检索：

Sedentary behaviour may be associated with cardiometabolic and reproductive health risks, but existing evidence should be described cautiously unless supported by prospective or genetic studies.
```

预期结果：

1. 生成 `zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/` 目录。
2. 目录中至少有：
   - `*_evidence_review.md`
   - `*_references.ris`
3. Markdown report 中有 `Citation Support Ledger`。
4. 如果 PubMed MCP 可用，PubMed 候选应有 PMID inspection；如果不可用，报告应写 `PubMed: ⚠️ Tool unavailable; search not executed`。
5. RIS 文件只包含 plain RIS records，不包含 Markdown 标题或解释文字。

如果只想测试聊天版，不想写文件：

```text
/zotero-evidence-review 只在聊天输出，不要生成文件：帮我给下面这句话找证据并说明可引用哪些文献。
```

---

## 4. 安装目标与同步方式

`bash scripts/install-skill.sh` 用于把仓库中的最新版 skill 同步到不同 skill 目录，避免“仓库版本已更新，但全局安装版本仍是旧版”的漂移问题。默认目标是 Codex，默认安装 `zotero-evidence-review`；可用 `--skill zotero-literature-learning` 安装 Zotero 素材学习层，或用 `--skill all-skills` 一次安装全部四个 skill。

### 4.1 安装到不同目标

```bash
# Codex 全局目录（当前 Codex 会话使用的 skill 目录）
bash scripts/install-skill.sh --skill all-skills --target codex --prune-backups

# ZCode 全局目录（推荐给 ZCode 用户；默认安装 zotero-evidence-review）
bash scripts/install-skill.sh --target zcode --prune-backups

# 安装独立 PubMed literature search skill
bash scripts/install-skill.sh --skill pubmed-literature-search --target zcode --prune-backups

# 一次安装全部 skill
bash scripts/install-skill.sh --skill all-skills --target zcode --prune-backups

# OpenCode 全局目录（推荐给 OpenCode 用户）
bash scripts/install-skill.sh --target opencode --prune-backups

# 当前仓库项目级 OpenCode skill 目录
bash scripts/install-skill.sh --target project --prune-backups

# 同时同步到 Codex + ZCode + OpenCode + 项目级目录
bash scripts/install-skill.sh --target all --prune-backups
```

### 4.2 目标路径

| `--target` | 安装路径 |
|---|---|
| `codex` | `~/.codex/skills/<skill-name>` |
| `zcode` | `~/.zcode/skills/<skill-name>` |
| `opencode` | `~/.config/opencode/skills/<skill-name>` |
| `project` | 当前仓库的 `.opencode/skills/<skill-name>` |
| `all` | 同步到以上四个位置 |

### 4.3 备份与去重规则

加上 `--backup` 后，如果目标目录已存在，脚本会先创建备份：

```text
zotero-evidence-review.backup-YYYYmmdd-HHMMSS
```

然后再覆盖安装。需要保留回滚副本时使用 `--backup`；日常同步建议使用 `--prune-backups`，安装成功后会删除所选目标下该仓库技能产生的时间戳备份。它只处理 `zotero-evidence-review.backup-*`、`zotero-literature-learning.backup-*`、`zotero-manuscript-thinking.backup-*` 和 `pubmed-literature-search.backup-*`，不会触碰其它 Skill 或 Zotero 数据。

只想先查看、不删除时运行：

```bash
python3 scripts/cleanup-installed-skills.py --target codex
```

确认后再加 `--apply`。安装状态检查会把残留备份报告为漂移；严格门禁下会返回失败：

```bash
python3 scripts/check-installed-skills.py --target codex --mode fail
```

### 4.4 更新后确认当前会话使用的是新 skill

修改仓库中的 `SKILL.md` 不会自动更新已经安装到 `~/.codex/skills/`、`~/.zcode/skills/` 或 OpenCode 目录中的旧副本。每次修复 workflow、MCP guardrail 或输出模板后，请重新运行安装脚本同步目标目录，例如：

```bash
bash scripts/install-skill.sh --skill all-skills --target codex --prune-backups
```

同步后请完全重启 Codex / ZCode / OpenCode 或开启新会话；仅刷新当前聊天通常不会重新加载 skill 与 MCP tool 列表。若仍看到 `Tool skipped because a previous tool call in the scheduled sequence failed`，先检查同一批工具调用中第一个失败的 MCP 调用，并确认当前会话加载的是同步后的 skill 副本。

可用下面的只读命令确认 installed copy 是否与仓库一致：

```bash
python3 scripts/check-installed-skills.py --target all --mode warn
```

若报告 `different`、`missing` 或 `timestamped backup copies remain`，先重新运行 `bash scripts/install-skill.sh --skill all-skills --target ... --prune-backups`，再重启客户端。

---

## 5. 配置 Zotero MCP

`zotero-evidence-review` 需要通过 Zotero MCP 访问 Zotero 本地库。

### 5.1 安装 zotero-mcp

推荐使用 `pipx`：

```bash
pipx install "zotero-mcp-server[all]"
```

也可以使用 `uv`：

```bash
uv tool install "zotero-mcp-server[all]"
```

安装后检查：

```bash
which zotero-mcp
zotero-mcp version
```

如果命令找不到，请确认 `pipx` / `uv` 的 bin 目录已经加入 `PATH`。

### 5.2 Agent IDE MCP 配置总原则

`zotero-evidence-review` 只依赖“当前会话中可见的 MCP tools”，不绑定某一个客户端。OpenCode、ZCode、Claude Desktop、Cherry Studio 等 Agent IDE 都可以使用，但它们的配置文件路径和 JSON 结构并不相同，不能把某个客户端的示例原样复制到另一个客户端。

| 客户端 | 常见配置位置 | MCP 配置形态 |
|---|---|---|
| OpenCode | `~/.config/opencode/opencode.json` | 顶层 `mcp`，server 名直接放在 `mcp` 下 |
| ZCode v2 | `~/.zcode/v2/config.json` | 顶层 `mcp`，server 名直接放在 `mcp` 下 |
| ZCode CLI 旧配置/兼容层 | `~/.zcode/cli/config.json` | `mcp.servers` |
| Claude Desktop / 部分 GUI 客户端 | 客户端自己的配置文件 | 常见为 `mcpServers` |

配置完成后必须重启对应 Agent IDE 或开启新会话；只要工具列表里能看到 Zotero / PubMed 相关 MCP tools，skill 就能调用。

### 5.3 OpenCode MCP 配置示例

OpenCode 配置文件通常位于：

```text
~/.config/opencode/opencode.json
```

示例配置：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "zotero": {
      "type": "local",
      "command": ["/path/to/zotero-mcp", "serve"],
      "environment": {
        "ZOTERO_LOCAL": "true"
      },
      "enabled": true
    }
  }
}
```

把 `/path/to/zotero-mcp` 替换为：

```bash
which zotero-mcp
```

输出的真实路径。

### 5.4 ZCode MCP 配置方式

ZCode 有多个配置层。当前桌面版 / v2 主要读取：

```text
~/.zcode/v2/config.json
```

配置形态与 OpenCode 类似，使用顶层 `mcp`：

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
    }
  }
}
```

部分 ZCode CLI / 旧配置仍可能使用：

```text
~/.zcode/cli/config.json
```

并采用 `mcp.servers` 形态：

```json
{
  "mcp": {
    "servers": {
      "zotero": {
        "type": "stdio",
        "command": "/path/to/zotero-mcp",
        "args": ["serve"],
        "environment": {
          "ZOTERO_LOCAL": "true"
        },
        "enabled": true
      }
    }
  }
}
```

如果通过 ZCode 界面添加 MCP Server，也要确认最终写入的是当前 ZCode 实际读取的配置层。修改配置后请完全重启 ZCode；仅刷新当前聊天通常不会重新加载 MCP。

更多配置细节见：[Zotero_MCP_OpenCode_Guide.md](./Zotero_MCP_OpenCode_Guide.md)。

---

## 6. 构建与更新语义索引

语义搜索依赖 zotero-mcp 的本地索引。首次使用前建议构建一次。

```bash
# 快速索引：主要处理元数据，适合首次测试
zotero-mcp update-db

# 全文索引：更适合证据核实和段落补引用，但耗时更长
zotero-mcp update-db --fulltext

# 查看索引状态
zotero-mcp db-status
```

高级排障时才建议使用强制重建：

```bash
zotero-mcp update-db --force-rebuild
```

> 注意：在 skill 工作流中，健康检查默认只读，不会自动重建索引。只有用户明确确认后，才应执行索引更新或强制重建等维护操作。

---

## 7. 使用教程与提示词示例

安装并配置完成后，在 OpenCode / ZCode 中直接对话即可。基于 Zotero 本地库找证据时用 `/zotero-evidence-review` 开头；直接检索 PubMed、检查 PMID 或导出 PubMed-only RIS 时用 `/pubmed-literature-search` 开头。

推荐短提示词：

```text
/zotero-evidence-review 帮我给下面这段草稿找证据并补引用：……
```

```text
/zotero-evidence-review 帮我导出 Evidence Package：Markdown 报告 + EndNote RIS。
```

```text
/zotero-evidence-review 只在聊天输出，不要生成文件：帮我分析这段话的证据和推荐引用。
```

```text
/pubmed-literature-search 检索近 5 年 PCOS 与 sedentary behavior 相关的 PubMed 文献，列出可引用的关键研究。
```

```text
/pubmed-literature-search 根据 PMID 12345678 找 related reviews，并导出 Markdown 报告和 EndNote RIS。
```

如果不用 slash command，也可以直接说“帮我补引用”“帮我导出 Evidence Package”“帮我直接检索 PubMed”等自然语言需求；只要意图清楚，skill 会自动路由。

### 7.0 端到端运行总览

把 workflow 想成两层：

1. **Zotero-first**：先用你的本地 Zotero 库找可追踪证据，保留 Zotero item、PDF、notes、collection 和本地上下文。
2. **PubMed-auto when visible**：生物医学主题会在 Zotero 本地检索后自动尝试当前会话可见的 PubMed MCP；不可见时只给可复制 query，不声称已完成检索，也不生成 PubMed-only RIS。

最常用的完整路径如下：

```text
安装/同步 skill → 配置 Zotero MCP → 构建语义索引 → 在 ZCode/OpenCode 中发起请求 → intent routing → Zotero local search → paragraph/search evidence analysis → PubMed auto expansion when visible → citation support / PMID inspection ledgers → metadata QC → Markdown report + EndNote RIS
```

| 需求类型 | 默认路线 | PubMed MCP 用法 | 文件输出 | 最省事提示词 |
|---|---|---|---|---|
| 找文献 / 主题综述 | `zotero-evidence-review` Module 1：Zotero 语义+结构检索 | 生物医学主题在 Zotero 后自动扩展 | 默认生成 search Markdown report + Search RIS | `搜 Zotero 库中关于 {topic} 的论文，列出最相关的 10 篇。` |
| 直接 PubMed 主题检索 / PMID 检查 | `pubmed-literature-search`：PubMed search → PMID metadata → optional related/review expansion → Zotero cross-check when visible | 作为主检索层，必须实际调用 PubMed MCP 才能标记 Completed | 默认生成 PubMed review + RIS | `检索近 5 年 {topic} 的 PubMed 文献。` |
| 段落找证据、找引文、补引用 | `zotero-evidence-review` Module 2 → Module 2.5 完整 Paragraph Citation Package Workflow | Zotero 本地检索后自动 PubMed expansion；按 DOI/PMID 去重 | 默认生成 Markdown report + EndNote RIS | `帮我给下面这段草稿找证据并补引用，生成 Evidence Package：...` |
| 已有编号引用修复 | `zotero-evidence-review` Existing Numbered Citation Repair | 需要替换或补充 biomedical references 时扩展 | 默认生成 Markdown report + 最终 RIS | `检查并更新下面这段已有编号引用，指出不支持的引用并修复：...` |
| 精确核实某条引用是否支持某主张 | `zotero-evidence-review` Module 3：读取元数据/全文并逐条判断 | 仅在需要 PMID 元数据、外部摘要或 OA/full-text triage 时使用 | 默认聊天输出 | `核实 文献=... 是否支持 claim=...，优先读取全文。` |
| 库状态、索引、PDF 覆盖率 | `zotero-evidence-review` Module 0.5：只读健康检查 | 不需要 PubMed | 不导出，除非用户另行要求 | `做一次 Zotero library health check，只读检查。` |
| 只想快速看看，不要文件 | 对应模块的 chat-only 路线 | 可用则标注实际 PubMed 状态 | 不生成文件 | `只在聊天输出，不要生成文件：...` |

语言与格式约定：

- 保存的 Markdown 结果报告默认 **中文优先**：标题、解释、综合建议、风险提示、metadata QC 说明用中文。
- 英文论文草稿的 `Recommended Manuscript Text` / 润色段落可继续保持英文；中文草稿保持中文，除非用户明确要求翻译。
- 文章标题、期刊名、作者名、DOI、PMID、Zotero key、URL、数据库名等官方元数据保持原文/官方格式，通常不翻译。
- EndNote 导入文件默认是 **RIS**，不是 EndNote XML；`.ris` 文件必须只包含标准 RIS records，不加入 Markdown 标题、中文解释、代码围栏或注释。

几个关键规则：

- 段落找证据、找引文、补引用、推荐 citation placement，或用一句话请求可复用写作输出时，默认进入完整 **Paragraph Citation Package Workflow (Module 2 + Module 2.5)** 并写出两个文件。
- `/zotero-evidence-review` 是推荐入口；后面只需用一句话说清楚“找证据、补引用、导出报告、核实引用或检查库状态”，不需要手动选择模块。
- 如果只想在聊天中查看证据矩阵、推荐引用和 diff 段落，请在请求中明确写 `不要生成文件`、`只在聊天输出`、`不导出` 或 `chat only`。
- PubMed 只在当前环境确实配置并可见 PubMed-capable MCP 工具时才会执行；不可用时报告 query 和 `⚠️ Tool unavailable; search not executed`。
- Evidence Package 由 agent 按 workflow 生成；本仓库脚本负责安装同步和静态校验，不是独立的 RIS/report 生成 CLI。

### 7.1 场景 A：从零开始找文献

适合：刚确定选题，想先知道 Zotero 库里有什么可用文献，并默认得到可复用的检索报告和 RIS。

```text
/zotero-evidence-review 搜 Zotero 库中关于 CRISPR base editing off-target effects 的论文，列出最相关的 10 篇，并说明每篇适合支持什么主张。
```

默认会写入 `zotero-evidence-output/.../*_literature_search.md` 和 `*_references.ris`；如果只想在聊天中预览结果，请改成 `只在聊天输出，不要生成文件：搜 Zotero 库中关于 ...`。

```text
/zotero-evidence-review 查找 Zotero 中关于 climate change and cardiovascular health 的文献，并按研究类型分组：综述、队列研究、机制研究、临床研究。
```

想限制范围时，加 collection 或 tag：

```text
/zotero-evidence-review 只在我的 “AI in Medicine” collection 中搜索 large language models for clinical decision support 的文献，按相关性排序。
```

```text
/zotero-evidence-review 查找带有 systematic-review 或 meta-analysis 标签、主题与 inflammation and atherosclerosis 相关的条目。
```

### 7.2 场景 B：给草稿段落补引用（推荐完整工作流）

默认行为：当你用 `/zotero-evidence-review` 或直接说“找引文、补引用、推荐引用、citation placement”时，skill 会执行一个完整的 **Paragraph Citation Package Workflow**，而不是拆成两个独立流程。只有明确写 `不要生成文件`、`只在聊天输出`、`不导出` 或 `chat only`，才会停在聊天版段落分析。

```text
paragraph → claim extraction → Zotero local search → evidence matrix + citation placement + diff paragraph → PubMed expansion → Zotero/PubMed matching + metadata QC → Markdown report + EndNote RIS
```

PubMed expansion 会在 Zotero 本地检索后自动尝试执行，但前提是当前环境确实配置并可见 PubMed-capable MCP 工具。

```text
/zotero-evidence-review 帮我给下面这段论文草稿找证据并补引用，生成 Markdown evidence report 和 EndNote RIS：

「慢性炎症通过激活 JAK-STAT 通路促进动脉粥样硬化进展，并可能增加心血管事件风险……」
```

只在聊天中输出的示例：

```text
/zotero-evidence-review 只在聊天输出，不要生成文件：帮我给下面这段论文草稿做证据链分析并补引用。

「慢性炎症通过激活 JAK-STAT 通路促进动脉粥样硬化进展，并可能增加心血管事件风险……」
```

### 7.3 场景 C：已有编号引用，检查并修复

适合：稿件里已经有 `[6,18]` 或上标编号，但你怀疑某些文献只是背景、并不直接支持原句。workflow 会优先做 `Existing Numbered Citation Repair`：逐条映射 `citation number → supplied reference metadata → claim`，判断 `Keep / Replace / Remove / Verify / Add supporting citation`，再导出 Markdown 报告和最终 RIS。原始编号只作为审计字段保留；导入 EndNote/Word 后最终编号由引用管理器重排。

```text
/zotero-evidence-review 帮我检查并更新下面这段已有编号引用，逐条判断每个编号是否支持原句；不支持的引用请替换或改成 background only；最后生成 Markdown evidence report 和 EndNote RIS：

Several genetic observations were consistent with a directional contribution of sedentary behavior to PCOS susceptibility6,18. ...

6. Wang Z, Emmerich A, Pillon NJ, et al. Genome-wide association analyses of physical activity and sedentary behavior provide insights into underlying mechanisms and roles in disease prevention. Nat Genet. 2022;54(9):1332–1344.
18. Shao C, Yang Q, Huang L, et al. Sex-Stratified Genetic Analyses Mapping the Influences of Sedentary Behaviors and Physical Activity on Female Reproductive Health. Research (Wash D C). 2026;9:1131.
19. Wang C, Wu W, Yang H, et al. Mendelian randomization analyses for PCOS: evidence, opportunities, and challenges. Trends Genet. 2022;38(5):468–482.
```

在这种模式下，若 #6 只支持 sedentary-behavior GWAS/background 而不直接支持 PCOS directional susceptibility claim，报告应将 #6 标为 `partial / no`，给出 `Replace` 或 `Background only` 建议，并默认从最终 RIS 中排除或标记为 Optional。

### 7.4 场景 D：直接使用 PubMed

适合：你不想依赖 Zotero，或者需要快速做 PubMed-only 检索、PMID 检查、related/review discovery、OA 全文可用性检查。

```text
/pubmed-literature-search 检索近 5 年 PCOS 与 sedentary behavior 相关的 PubMed 文献，检查 PMID 元数据，列出可引用研究，并导出 Markdown 报告和 EndNote RIS。
```

```text
/pubmed-literature-search 根据 PMID 12345678 找 similar articles 和 related reviews；优先综述、队列研究和遗传学研究；最后导出 RIS。
```

注意：PubMed 搜索结果 snippet 只是发现线索。只有经过 PMID metadata inspection 的条目，才应进入 PubMed-only RIS。

### 7.5 场景 E：Evidence Package 导出

Evidence Package 是 **Paragraph Citation Package Workflow** 的导出阶段，由 OpenCode / ZCode agent 按 `zotero-evidence-review` workflow 执行：agent 负责 Zotero 本地检索、PubMed 可见时自动扩展、匹配质控、写入 Markdown 与 RIS。段落补引文/写作证据包没有独立生成 CLI；仓库脚本负责安装同步、静态校验、RIS lint 和 output audit。另一个场景“目标文献检索清单”有独立 Phase 3 writer，见 [8.4 Target Literature Search Package](#84-target-literature-search-package)。

完整导出流程：

```text
paragraph/search → claim extraction or search synthesis → Zotero local search → canonical Zotero metadata + PDF links → automatic PubMed expansion as a second evidence source when available → PMID inspection for PubMed candidates → combined evidence synthesis and deduplication → Citation Support Ledger for every recommended citation/RIS candidate → reference export standardization by PMID/DOI → metadata QC → Markdown evidence report + EndNote RIS
```

运行检查点：

1. Zotero 条目进入报告或 RIS 前，必须读取 canonical metadata；不要凭记忆补齐作者、标题、期刊、年份、DOI 或 PMID。
2. Zotero 本地检索和 PubMed 扩展是两个证据来源步骤；报告中分别标记 `Zotero`、`PubMed` 或 `Zotero + PubMed`。
3. Zotero 和 PubMed 结果必须按 DOI、PMID、规范化标题和作者+年份+期刊去重，避免同一文献重复进入推荐列表。
4. 每个推荐 citation、citation placement、编号引用修复候选或 RIS candidate 都必须进入 **Citation Support Ledger**，形成 `claim/sentence → recommended citation → inspection route → evidence location → support verdict → RIS action` 的审计链。
5. `not inspected`、`contradicts`、`not addressed` 的 Citation Support Ledger 行默认不得进入 RIS；应标记 `Exclude` 或 `Verify`。`background only` 只能作为 Optional，或在稿件文字明确写成背景/语境时才可 Include。
6. PubMed 搜索 snippet 不能直接成为推荐 citation 或 PubMed-only RIS record；推荐或导出的 PMID 必须先完成 PMID Inspection Ledger，并通过 `pubmed_get_details`、`pubmed_extract_info` 或等价可见元数据工具检查。
7. RIS 导出阶段再用 PMID/DOI 重新标准化参考文献元数据：优先 PMID/PubMed，其次 DOI；无法在线核验时使用已检查的 Zotero 或 PubMed 来源元数据。
8. PubMed 状态必须写清：`Completed`、`⚠️ Tool unavailable; search not executed` 或 `Failed; query reported`。
9. RIS 必须是 plain RIS records；不要混入 Markdown 标题、解释文字、代码围栏或注释。
10. 最终聊天回复只列出生成文件路径和关键 warnings，不重复整份报告。

```text
/zotero-evidence-review 请围绕下面这段讨论生成 Evidence Package：自动检索 Zotero 证据，PubMed MCP 可见时自动扩展，保存 Markdown 证据报告，并生成可导入 EndNote 的 RIS 文件。

「久坐行为可能与 PCOS 发生风险相关，但既往队列研究证据仍不一致……」
```

默认只生成两个文件，并放入能体现 skill 来源的固定输出根目录；每次运行再用 LLM 简短主题概括 + 日期时间后缀创建专门目录：

```text
zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_evidence_review.md
zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_references.ris
```

`brief_topic_slug` 由 agent 根据用户段落、claim 或检索问题自动概括，应短而具体，例如 `sedentary_behavior_pcos`，不要使用 `topic`、`references`、`output` 等泛名。`YYYY-MM-DD_HHMMSS` 使用当前本地日期时间到秒；如果同名目录已存在，使用 `_v2`、`_v3` 等目录后缀，默认不覆盖旧结果。

RIS 导出会过滤 Zotero 个人/流程标签（例如 emoji、纯符号、`/reading` 这类以 `/` 开头的标签），只保留学术关键词，以提高 EndNote 导入兼容性。

如果当前环境未配置 PubMed-capable MCP 工具，skill 只会输出可复制 PubMed query，并标注 `⚠️ Tool unavailable; search not executed`；不会声称已完成 PubMed 检索，也不会生成 PubMed-only RIS records.

### 7.6 场景 F：核实某个 claim 是否被文献支持

```text
请核实这篇文献是否真的支持以下主张：
主张：IL-6 receptor blockade reduces cardiovascular event risk in patients with chronic inflammation.
文献：给定 DOI / Zotero key / 标题
请读取元数据和全文，判断 fully supported、partially supported、contradicted 或 not addressed，并引用原文证据。
```

### 7.7 场景 G：Zotero 库健康检查

```text
帮我做一次 Zotero library health check：检查语义索引、PDF 覆盖率、重复条目和缺失摘要。只读检查，不要修改任何条目。
```

### 7.8 场景 H：从全文角度做论证与修订策略检查

局部润色解决的是句子，`zotero-manuscript-thinking` 解决的是“这篇论文整体上应该先改什么”。它先做意义保持和语言精确度检查，再检查 Introduction 的 `context → known → gap → method fit → contribution` 链、Methods 的 `design → sample/variables → procedure → QC/statistics → ethics/data` 链、Results 的 `setup/QC → primary finding → support/sensitivity → validation` 链，以及 Discussion 的 `finding → interpretation → literature comparison → alternative/limitation → bounded implication` 链；随后建立 `paper contract`、重建五句 `argument spine`，把核心 claim 映射到章节/图表/证据，再按 `thinking-model-router` 选择一个主思考模型。只有主模型留下实质盲点时，才增加第二个模型。

```text
/zotero-manuscript-thinking
请从全文角度审视这篇论文：
1. 重建 paper contract 和 argument spine；
2. 检查 Current study、Zotero/PubMed external evidence 和 Interpretive bridge 是否混淆；
3. 从审稿风险、论证杠杆和可行性排序 P0/P1/P2/P3 问题；
4. 给出最多三轮的修改顺序和每轮完成标准；
5. 不要直接重写全文，也不要自动承诺新实验。
```

在段落补引用或已有编号引文修复中，如果段落属于完整稿件、局部修改已重复两轮，或出现证据等级 E/强因果/主张无结果位置等高风险信号，`zotero-evidence-review` 会先运行紧凑 checkpoint，再给出 Copy-ready text。只有单个段落时会明确标记为 scope-limited checkpoint。

如果你要求“语言要地道”或“像这个领域的代表性论文”，checkpoint 会额外建立一个小型 `Domain Style Calibration`：优先从 Zotero 选取 3–5 篇同领域、同文章类型、同目标 section 的可检查论文，依次执行 `zotero_get_recent → zotero_semantic_search → zotero_get_item_metadata → zotero_get_item_children → zotero_get_pdf_outline → zotero_read_pdf_pages`，提取段落功能、句子功能、术语、claim verbs、引用归属和信息节奏。Methods 还会比较可复现细节的组织顺序和报告规范；Results 还会比较主要/支持结果的排序、定量锚点、图表连接和解释边界，再把你的草稿与这些模式做对照。它只学习写作决策，不复制原文，也不会用 peer paper 替你的研究补结果或贡献。语料不足时报告 `calibration_confidence: low/none`，继续做 genre-neutral 的语言诊断。

### 7.9 场景 I：Zotero 证据不足时的外部兜底

```text
如果 Zotero 库里证据不足，请说明缺口，并在外部工具可用时给出 Crossref / OpenAlex / PubMed 检索建议；如果工具不可用，只输出可复制的检索式，不要声称已经完成外部检索。
```

---

## 8. 推荐输出格式

Skill 内置了多个输出模板。普通对话可使用 Refs block、claim-evidence matrix 和 diff paragraph；当用户要求保存、导出 EndNote、生成 Evidence Package，或用 `/zotero-evidence-review` 进行段落找引文、补引用、推荐引用、citation placement 时，默认使用完整的 **Paragraph Citation Package Workflow (Module 2 + Module 2.5)**：Zotero 本地检索后自动尝试 PubMed expansion（工具可用时），再生成 Markdown report 和 RIS；除非用户明确要求 `不要生成文件` 或 `只在聊天输出`。

默认导出文件只有两类，并写入 `zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/` 目录：`{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_evidence_review.md` 和 `{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_references.ris`。`brief_topic_slug` 由 agent/LLM 对主题自动做简短概括。不要额外生成 JSON、BibTeX、EndNote XML、DOI 清单或日志文件，除非用户明确要求。

### 8.1 Evidence Package report

Markdown 报告是主要阅读界面，顶部必须明确 PubMed 是否实际执行，Reference Table 应显示证据来源（`Zotero`、`PubMed`、`Zotero + PubMed`），Metadata QC 应显示 RIS standardization source：

```markdown
# 证据综述：{topic}

生成日期：{YYYY-MM-DD}
来源：Zotero 本地库；PubMed: {Completed / ⚠️ Tool unavailable; search not executed / Failed; query reported / Not executed only for explicit chat-only or non-PubMed workflows}
输入：{user paragraph, claim, or search question}

## 1. Metadata and Use Status
## 2. Critical Warnings
## 3. Bottom Line
## 4. Copy-ready Manuscript Text
## 5. Annotated Recommended Text
## 6. Claim–Evidence Matrix
## 7. Citation Placement
### Citation Support Ledger
## 8. Evidence Logic Chain
## 9. Reference Table
## 10. Search Reproducibility
## 11. Zotero Search Summary
## 12. PubMed Expansion
## 13. Integrated Writing Advice
## 14. Claims to Revise or Remove
## 15. Gaps and Reviewer-risk Assessment
## 16. Metadata Quality Control
## 17. Export File
```

`Citation Support Ledger` 嵌入在 Markdown report 的 Citation Placement 部分，而不是默认生成单独文件。它至少包含：`Claim / sentence`、`Recommended citation`、`Source layer`、`Evidence level`、`Inspection route`、`Evidence location`、`Support verdict`、`RIS action`、`Required wording/action`。该表是 copy-ready text、annotated text、Citation Placement、Reference Table、Metadata QC、RIS 之间的可审计桥梁；它帮助发现“推荐引用未核查”“只支持背景却被写成直接证据”“不支持却进入 RIS”等问题，但不替代人工/全文级语义判断。

### 8.2 Reference Table

Zotero item key 不作为主要阅读对象展示，只隐藏在可点击链接中；DOI 和 PMID 尽量用链接呈现。

```markdown
| # | Citation | Year | Study type | Main use | Evidence source | Zotero | PDF | DOI | PMID | Collection |
|---|----------|------|------------|----------|-----------------|--------|-----|-----|------|------------|
| 1 | Author et al., *Journal* | 2024 | Systematic review | ... | Zotero + PubMed | [Item](zotero://select/items/0_KEY) | [PDF](zotero://open-pdf/library/items/ATTACHMENT_KEY) | [DOI](https://doi.org/10.xxxx/xxxx) | [PMID](https://pubmed.ncbi.nlm.nih.gov/PMID/) | Collection name |
```

### 8.3 PubMed Expansion

PubMed 是 Paragraph Citation Package Workflow 中的自动扩展步骤：段落引文导出、普通生物医学检索和目标文献检索时，skill 会在 Zotero local search 后自动尝试 PubMed expansion；只有当前环境确实配置并可见 PubMed-capable MCP 工具时，才能声称已完成 PubMed 检索。

#### PubMed 工具配置

本仓库不内置 PubMed MCP server。**结论是：需要你先把 PubMed MCP server 配置到你正在使用的 Agent IDE；`zotero-evidence-review` 和 `pubmed-literature-search` 都只负责识别并调用当前会话中已经可见的 PubMed 工具。** README 只保留 quickstart 和协同原则；完整安装、构建、launcher、NCBI API key 与 smoke-test 细节请以 [`docs/PANCREPAL_PUBMED_MCP_GUIDE.md`](./docs/PANCREPAL_PUBMED_MCP_GUIDE.md) 为准。

不要把 OpenCode、ZCode、Claude Desktop、Cherry Studio 等客户端的 MCP 配置示例混用：它们的配置路径和 JSON 形态可能不同。常见区别如下：

| 客户端 | 常见配置位置 | MCP 配置形态 |
|---|---|---|
| OpenCode | `~/.config/opencode/opencode.json` | 顶层 `mcp`，server 名直接放在 `mcp` 下 |
| ZCode v2 | `~/.zcode/v2/config.json` | 顶层 `mcp`，server 名直接放在 `mcp` 下 |
| ZCode CLI 旧配置/兼容层 | `~/.zcode/cli/config.json` | `mcp.servers` |
| Claude Desktop / 部分 GUI 客户端 | 客户端自己的配置文件 | 常见为 `mcpServers` |

配置完成后必须完全重启对应 Agent IDE 或开启新会话；只要当前工具列表里能看到 PubMed / NCBI 相关 MCP tools，skill 就能调用。若工具不可见，Evidence Package 必须写 `PubMed: ⚠️ Tool unavailable; search not executed`，不能因为生成了 PubMed query 就声称已完成检索。

可以把两件事理解为分层：

| 层级 | 负责什么 | 是否由本 skill 内置 |
|------|----------|--------------------|
| PubMed MCP server | 连接 PubMed / NCBI、执行 search / fetch / fulltext / export 等工具调用 | 否，需要单独安装配置 |
| `zotero-evidence-review` skill | 在 Zotero local search 后生成 PubMed query、调用可见 PubMed 工具、合并 Zotero/PubMed 结果、去重、写 Evidence Report + RIS | 是 |
| `pubmed-literature-search` skill | 直接以 PubMed MCP 为主检索层，执行主题检索、PMID metadata inspection、related/review expansion、OA full-text triage，并可导出 PubMed review + RIS | 是 |

当前已知可接入方案有两类：

1. **PancrePal-xiaoyibao/mcp-pubmed-server-pancrpal**：Node.js 版，功能较完整，当前常见工具包括 `pubmed_search`、`pubmed_get_details`、`pubmed_extract_info`、`pubmed_find_related`、`pubmed_detect_fulltext`、`pubmed_download_fulltext`、`pubmed_system_status`、`pubmed_manage_cache`。适合 `zotero-evidence-review` 的默认 PubMed 扩展层。
2. **andybrandt/mcp-simple-pubmed**：Python 版，部署更轻，适合基础 PubMed 搜索与论文详情/全文获取。

二选一即可；不要在没有需要时同时启用多个 PubMed MCP，以免 agent 面对多个相似工具时路由混乱。

##### Zotero + PubMed 推荐协同方式

| 阶段 | 首选 MCP | 使用方式 |
|---|---|---|
| 本地证据检索 | Zotero MCP | 先用语义/关键词/collection/tag 检索用户本地库，保留 Zotero item、PDF、notes、annotations 与 collection 上下文。 |
| 生物医学外部扩展 | PubMed MCP | 用 `pubmed_search` 扩展 Zotero 未覆盖的医学文献，并在报告中单独标记 `PubMed` 来源。 |
| 关键文献追踪 | PubMed MCP | 对高相关 PMID 使用 `pubmed_find_related` 查 similar/reviews，避免只靠关键词遗漏综述或邻近机制。 |
| 元数据标准化 | PubMed MCP + Zotero MCP | 有 PMID 时优先 `pubmed_get_details`，没有 PMID 但有 DOI 时走 DOI 元数据；Zotero 条目仍保留本地链接。 |
| 全文/OA 检测 | PubMed MCP | 需要全文时先 `pubmed_detect_fulltext`，只有 OA 可用且有必要时再 `pubmed_download_fulltext`；下载物不自动等同 Zotero 附件。 |
| RIS/EndNote 导出 | 可见工具优先 | 如果 PubMed MCP 当前暴露 RIS/NBIB/EndNote/BibTeX exporter，则优先用它处理 PubMed-only records；否则从 `pubmed_get_details` 已检查元数据生成 RIS。 |

##### 获取并配置 NCBI API key

PubMed MCP 可以匿名访问 PubMed，但匿名模式通常约 3 次/秒；配置 NCBI API key 后通常约 10 次/秒，更适合批量检索、详情抓取和全文/OA 检测。

1. 打开 `https://account.ncbi.nlm.nih.gov/settings/`。
2. 登录或注册 NCBI 账户。
3. 找到 `API Key Management`，点击 `Create an API Key`。
4. 复制生成的 key，并准备一个真实可联系邮箱作为 `PUBMED_EMAIL`。
5. 不要把真实 key 提交到 Git 仓库；只写入本机 `.env` 或 Agent IDE 的用户级配置文件。

##### 方案 A：PancrePal PubMed MCP（Node.js）

```bash
git clone https://github.com/PancrePal-xiaoyibao/mcp-pubmed-server-pancrpal.git ~/mcp-pubmed-server-pancrpal
cd ~/mcp-pubmed-server-pancrpal
npm install
npm run build
# 可选：匿名模式可不创建 .env；需要 API key 时再 cp .env.example .env 并填写 PUBMED_API_KEY / PUBMED_EMAIL
ABSTRACT_MODE=deep FULLTEXT_MODE=enabled MCP_TRANSPORT=stdio node dist/index.js
```

上面的 `node dist/index.js` 适合在终端中做一次本地 smoke test。ZCode / OpenCode 尤其是 GUI 启动时可能不继承 shell 的 `PATH`，因此长期配置建议使用绝对路径 launcher，而不是直接写裸 `node`。

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

请把 `/opt/homebrew/bin/node` 与 `/Users/daxuan/mcp-pubmed-server-pancrpal/dist/index.js` 替换为本机真实路径。看到类似 `PubMed MCP Server ... running on stdio`、`abstract=deep`、`fulltext=enabled` 后，再写入当前 Agent IDE 的 MCP 配置。下面示例使用匿名模式，不要求 `PUBMED_API_KEY` / `PUBMED_EMAIL`；如需 API key，可把这两个变量加入 `environment`。

OpenCode / ZCode v2 使用顶层 `mcp`：

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

ZCode CLI 旧配置/兼容层可能使用 `mcp.servers`：

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

Claude Desktop / 部分 GUI 客户端常见为 `mcpServers`，请按对应客户端文档改写，不要把 `mcpServers` 原样粘贴到 OpenCode 或 ZCode v2。

##### 方案 B：mcp-simple-pubmed（Python）

```bash
conda create -n simple-pubmed python=3.10
conda activate simple-pubmed
pip install mcp-simple-pubmed
python -m mcp_simple_pubmed
```

Agent IDE 顶层 `mcp` 配置示例：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "zotero": {
      "type": "local",
      "command": ["/Users/daxuan/.local/bin/zotero-mcp", "serve"],
      "environment": {
        "ZOTERO_LOCAL": "true"
      },
      "enabled": true
    },
    "simple-pubmed": {
      "type": "local",
      "command": ["/opt/miniconda3/envs/simple-pubmed/bin/python", "-m", "mcp_simple_pubmed"],
      "environment": {
        "PUBMED_EMAIL": "你的邮箱地址",
        "PUBMED_API_KEY": "你的NCBI API key"
      },
      "enabled": true
    }
  }
}
```

请把 Python 路径替换为你机器上真实路径，可用下面命令查看：

```bash
conda run -n simple-pubmed which python
```

##### 配置后验证

配置后重启 OpenCode / ZCode 会话，并检查 MCP 列表或当前工具清单里是否出现 PubMed/NCBI 相关工具。只有工具在当前会话可见时，报告里的 PubMed 状态才应写为 `Completed`。

```markdown
## 7. PubMed Expansion
Date: {YYYY-MM-DD}
Database: PubMed
Status: Completed / ⚠️ Tool unavailable; search not executed / Failed; query reported

Query:
~~~text
{copyable PubMed query}
~~~
```

当 PubMed 工具不可用时，只输出 query 与状态 `⚠️ Tool unavailable; search not executed`，不生成 PubMed-only RIS records。此时可复制报告中的 PubMed query 到 PubMed 网页手动检索，或先完成上述 MCP 配置后重新运行 `/zotero-evidence-review`。

### 8.4 Target Literature Search Package

目标文献检索与段落 Evidence Package 是两条不同路线。用户没有提供稿件段落，而是问“哪些文献使用了 X 数据/方法/表型”“检索 Zotero 中关于 X 的文献”“导出文献清单/RIS”时，应使用 `target_literature_search`，默认输出 `LITERATURE_SEARCH_REPORT` + Search RIS，而不是 Copy-ready Manuscript Text、逐句 citation placement 或 paragraph diff。

典型提示词：

```text
/zotero-evidence-review 哪些文献使用了大脑相关 GWAS 数据？请做 Topic Decomposition、Query Expansion、Core/Strong Related/Noise 分类，并导出 MD 和 RIS。
```

若只想聊天查看，不生成文件：

```text
/zotero-evidence-review 只在聊天输出，不要生成文件：检索 Zotero 中关于肠道菌群和抑郁症的文献，按 Core / Strong Related / Verify / Noise 分类。
```

如果候选文献已经由 agent 或人工检索、分类、检查元数据，并整理成 JSON/YAML，可用 Phase 3 writer 生成标准检索包：

```bash
python3 scripts/write_literature_search_package.py \
  --input scripts/fixtures/literature_search_package_sample.json \
  --output-root /tmp/zotero-lit-test \
  --slug brain_gwas \
  --timestamp 2026-07-07_120000
```

writer 的边界很明确：

- 它不调用 Zotero 或 PubMed，只格式化已检查候选。
- JSON 必须支持；YAML 只在当前 Python 环境已有 PyYAML 时支持，不新增依赖。
- 默认只把 `RIS action = Include` 且类别合格的记录写入 Search RIS。
- `--include-optional` 才会写入合格的 `Optional` 记录。
- `Exclude` 与 `Verify` 永远不写入 Search RIS。
- PubMed-only 条目必须有 `pubmed_status = Completed` 且 `metadata_inspected = true`。

输出路径格式：

```text
zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_literature_search.md
zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_references.ris
```

### 8.5 Reviewer-risk 与 Metadata QC

Reviewer-risk 应指向具体主张或句子，方便回到原文修改；Metadata QC 应在导出信息前独立显示。Reference Canonicalization Gate 应把 RIS 决策回连到 Citation Support Ledger：只有 support verdict 与 RIS action 一致、且元数据来源可追踪的条目，才应进入最终 RIS。

```markdown
## 15. Gaps and Reviewer-risk Assessment
| Affected claim / sentence | Risk | Severity | Evidence basis | Suggested fix |
|---------------------------|------|----------|----------------|---------------|
| ... | Overstating causal evidence | High | Observational evidence only | Replace causal wording with association wording |

## 16. Metadata Quality Control
| Citation | Missing metadata | Metadata mismatch | Duplicate warning | Evidence source | RIS standardization source | Citation Support Ledger link | RIS action |
|----------|------------------|-------------------|-------------------|-----------------|----------------------------|-------------------------------|------------|
| Author Year | DOI / PMID / pages / none | Possible metadata mismatch / none | Possible duplicate / none | Zotero / PubMed / Zotero + PubMed | PMID/PubMed / DOI / Zotero metadata / PubMed metadata | claim/sentence row | Include / Exclude / Verify / Optional |
```

### 8.6 RIS export snippet

RIS 文件必须是 plain RIS records，不要混入 Markdown 标题、说明文字、代码围栏或注释。

```ris
TY  - JOUR
AU  - Last, First
PY  - 2024
TI  - Article title
JO  - Journal name
DO  - 10.xxxx/xxxx
AN  - PMID
N1  - Zotero key: XXXXXXXX
ER  -
```

EndNote 导入建议步骤：

1. 在 EndNote 中选择 `File → Import → File`。
2. 选择 Evidence Package 目录中的 `*_references.ris`。
3. `Import Option` 选择 `Reference Manager (RIS)` 或 `RIS`。
4. `Text Translation` 选择 `UTF-8`。
5. 首次测试或担心污染现有 library 时，先导入一个空白 EndNote library。
6. 导入后检查重复项；必要时用 EndNote 的 duplicate 管理功能合并。

如果 EndNote 报错，先确认 `.ris` 文件没有 Markdown 标题、中文解释、代码围栏、emoji、个人流程标签或不完整 record；每条记录都应以 `TY  -` 开始，并以 `ER  -` 结束。

### 8.7 Chat-only templates

不需要保存文件时，可继续使用简短对话模板：`REFS_BLOCK`、`CLAIM_EVIDENCE_MATRIX`、`WRITING_SUGGESTIONS_TABLE`、`DIFF_REVISED_PARAGRAPH` 和 `VERIFICATION_REPORT`。完整规范以 `zotero-evidence-review/SKILL.md` 的 Appendix 为准。

## 9. 安全与可用性规则

本 skill 的设计重点是“可追溯”和“不过度声称”。

- **不伪造引用**：不得虚构 citation、DOI、PMID、Zotero key、标题、作者、期刊或年份。
- **健康检查只读**：默认只检查状态，不重建索引、不合并重复项、不改标签、不删除条目。
- **破坏性或批量操作需确认**：删除条目、批量改标签、合并重复项、移动 collection、覆盖 notes/annotations 前必须获得明确确认。
- **外部 MCP 工具需可用才使用**：Crossref、OpenAlex、Semantic Scholar、PubMed、CNKI/CDP、WebSearch 等外部工具只有在当前环境已配置时才能声称执行；否则只能提供可复制检索式。
- **PubMed 是条件能力**：段落引文导出时，PubMed expansion 是 Zotero 本地检索后的自动尝试步骤；但当前环境未配置且可见 PubMed-capable MCP 工具时，skill 只输出可复制 PubMed query，不声称已完成 PubMed 检索，也不生成 PubMed-only RIS records。
- **Citation Support Ledger 是强制审计链**：每个推荐 citation、编号引用修复候选和 RIS candidate 都应映射到 claim/sentence、inspection route、evidence location、support verdict 与 RIS action；`not inspected`、`contradicts`、`not addressed` 默认不得进入 RIS。
- **PMID Inspection Ledger 是 PubMed-only RIS 前置条件**：PubMed 搜索 snippet 只能作为发现线索，不能作为推荐 citation 或 RIS 依据；PubMed-only RIS 记录必须来自 `Inspection status = completed` 且无未解决 metadata/retraction warning 的 PMID Inspection Ledger 行。
- **Ledger 不等于语义真值证明**：Citation Support Ledger 与 PMID Inspection Ledger 是可审计记录和质量门禁输入，不会自动证明某篇文献真实支持某个 manuscript claim；关键主张仍需元数据、摘要、全文或人工复核。
- **不可用检查必须标注**：工具不可用、Zotero 未连接、查询不支持时，输出 `⚠️` 并解释限制，不估算、不编造数量。
- **全文证据优先**：核实具体主张时优先读取 PDF/全文；只有元数据不足以证明具体实验结论或统计结果。
- **输出与隐私卫生**：`zotero-evidence-output/` 中的 Markdown report 和 RIS 可能包含未发表稿件、Zotero 本地链接、笔记摘要、检索策略和待引用文献；除非明确打算共享，不要提交到 Git 或公开仓库。
- **密钥卫生**：不要提交 `PUBMED_API_KEY`、`PUBMED_EMAIL`、本机 MCP 私有配置、`.env` 或含真实 token 的截图。

---

## 10. 仓库结构

```text
zotero-skills/
├── README.md
├── Zotero_MCP_OpenCode_Guide.md
├── zotero-evidence-review/
│   └── SKILL.md
├── zotero-literature-learning/
│   ├── SKILL.md
│   └── references/materials-package-schema.md
├── zotero-manuscript-thinking/
│   └── SKILL.md
├── pubmed-literature-search/
│   └── SKILL.md
├── scripts/
│   ├── install-skill.sh
│   ├── cleanup-installed-skills.py
│   ├── validate-skill.py
│   ├── validate-manuscript-thinking.py
│   ├── validate-pubmed-skill.py
│   ├── check-all.py
│   ├── ris_lint.py
│   ├── smoke_prompts.py
│   └── write_literature_search_package.py
├── docs/
│   ├── DEVELOPMENT_PLAN.md
│   ├── DEVELOPMENT_PLAN00.md
│   └── ZOTERO_EVIDENCE_REVIEW_OUTPUT_PLAN.md
└── .opencode/                 # 安装脚本可生成；通常不需要手动维护
    └── skills/
        └── zotero-evidence-review/
```

| 路径 | 说明 |
|---|---|
| `zotero-evidence-review/SKILL.md` | 核心 skill 定义文件；当前工作流的权威规范。 |
| `zotero-literature-learning/SKILL.md` | Zotero MCP 素材收集、全文/摘要分层阅读、写作卡点学习、peer corpus 与 profile 交接。 |
| `zotero-manuscript-thinking/SKILL.md` | 全文论证、证据边界和修订优先级 checkpoint；由核心 Zotero skill 按条件调用。 |
| `pubmed-literature-search/SKILL.md` | 独立 PubMed MCP 文献检索 skill 定义文件。 |
| `scripts/install-skill.sh` | 安装/同步 skill 到 Codex、ZCode、OpenCode 或项目目录；可用 `--prune-backups` 清理本仓库产生的旧备份。 |
| `scripts/cleanup-installed-skills.py` | 默认只读盘点，按目标和仓库技能安全清理时间戳备份；必须显式加 `--apply` 才删除。 |
| `scripts/validate-skill.py` | 静态验证 Zotero skill 的元数据、章节、模板和安全防护说明；不执行 Zotero/PubMed 工作流。 |
| `scripts/validate-pubmed-skill.py` | 静态验证 PubMed literature search skill。 |
| `scripts/check-all.py` | 本地质量门：validator、writer self-test、可选 output audit/RIS lint/MCP config/installed drift/smoke prompt check。 |
| `scripts/write_literature_search_package.py` | Phase 3 target literature search package writer：从已检查候选 JSON/YAML 生成 `*_literature_search.md` 和 Search RIS。 |
| `scripts/fixtures/literature_search_package_sample.json` | Phase 3 writer 的最小可运行 fixture。 |
| `.opencode/skills/` | 运行 `bash scripts/install-skill.sh --target project` 后生成的项目级 OpenCode skill 目录。 |
| `Zotero_MCP_OpenCode_Guide.md` | 更详细的 Zotero MCP 与 OpenCode 配置指南。 |
| `docs/` | 规划、设计和历史文档；当前行为以 `README.md` 与 `zotero-evidence-review/SKILL.md` 为准。 |

---

## 11. 常见问题排查

### 11.1 Codex / ZCode / OpenCode 看不到 skill

请重新同步到对应目录：

```bash
# Codex
bash scripts/install-skill.sh --skill all-skills --target codex --prune-backups

# ZCode
bash scripts/install-skill.sh --target zcode --prune-backups

# OpenCode
bash scripts/install-skill.sh --target opencode --prune-backups
```

然后重启或刷新 Codex / ZCode / OpenCode 会话。确认目录存在：

```text
~/.zcode/skills/zotero-evidence-review
~/.config/opencode/skills/zotero-evidence-review
```

### 11.2 Zotero MCP 报 connection refused

常见原因：Zotero 没打开，或本地访问未启用。

检查：

1. 打开 Zotero。
2. 在 Zotero 设置中启用“允许其他应用程序访问 Zotero”。
3. 确认 MCP command 指向真实的 `zotero-mcp` 路径。
4. 重启 OpenCode / ZCode 会话。

### 11.3 语义搜索没有结果

先查看索引状态。以下是用户手动运行的 CLI 排障命令；与 skill 的只读健康检查不同，agent 不会在健康检查中自动重建索引，除非你明确确认维护操作。

```bash
zotero-mcp db-status
```

如果没有索引或索引过旧：

```bash
zotero-mcp update-db
zotero-mcp update-db --fulltext
```

如果刚更换嵌入模型或索引损坏，再考虑：

```bash
zotero-mcp update-db --force-rebuild
```

### 11.4 EndNote 导入 RIS 时提示 Database error

这类错误通常首先指向 EndNote 本地 library 被占用、锁定或损坏，不一定代表 RIS 文件本身错误。建议按顺序排查：

1. 关闭所有 EndNote 窗口，确认没有其他用户或同步进程正在写入同一个 library。
2. 重启 EndNote 后重试导入。
3. 新建一个空白测试 library，再导入同一个 RIS；如果新库可导入，原 library 可能需要 EndNote 的 `Tools → Recover Library`。
4. 如果新库也失败，再检查 RIS：必须是 plain RIS records，不能有 Markdown、代码围栏、说明文字、emoji 或个人流程标签。
5. 对只有 DOI/PMID 的记录，可在 EndNote 中用 DOI/PMID 重新检索作为备用方案；但 Evidence Package 的默认交付仍是 Markdown report + RIS。

### 11.5 重复条目检查提示库太大

如果 Zotero 库很大，重复项扫描可能提示需要缩小范围。此时按 collection 检查：

```text
请只在某个 collection_key 下查找重复条目。
```

或先让助手列出 collections，再选择一个 collection 范围进行检查。

### 11.6 GitHub Desktop 要求登录 `gh-proxy.com`

这通常是 Git 全局 URL rewrite 或 remote 地址被代理改写导致的。检查：

```bash
git remote -v
git config --global --get-regexp 'url\..*insteadOf'
```

如果看到类似：

```text
https://gh-proxy.com/https://github.com/
```

可以恢复官方 GitHub 地址：

```bash
git config --global --unset url.https://gh-proxy.com/https://github.com/.insteadOf
git remote set-url origin https://github.com/DaXuanGarden/zotero-skills.git
```

然后重新打开 GitHub Desktop 或重试 push。

---

## 12. 进阶文档

- [Zotero_MCP_OpenCode_Guide.md](./Zotero_MCP_OpenCode_Guide.md)：Zotero MCP 安装、OpenCode 配置、语义索引、CLI 使用和常见问题。
- [`docs/ZOTERO_EVIDENCE_REVIEW_OUTPUT_PLAN.md`](./docs/ZOTERO_EVIDENCE_REVIEW_OUTPUT_PLAN.md)：Evidence Package 输出设计和验收标准；部分文件名示例可能是历史规划，当前默认以 README/SKILL.md 为准。
- [`docs/DEVELOPMENT_PLAN.md`](./docs/DEVELOPMENT_PLAN.md)：skill 设计与开发计划，包含已实现和历史规划内容。
- [`docs/DEVELOPMENT_PLAN00.md`](./docs/DEVELOPMENT_PLAN00.md)：早期规划记录。

> 当前权威工作流规范：`zotero-evidence-review/SKILL.md`；当前用户安装与使用说明：本 README。

---

## 13. 贡献

欢迎通过 Issue 或 PR 改进：

- 新的 Zotero MCP 工作流；
- 更严格的引用核实模板；
- 中文学术写作场景；
- OpenCode / ZCode 安装体验；
- 自动同步、验证与测试脚本。

提交前建议运行：

```bash
python3 scripts/check-all.py --output-warnings skip --smoke-prompts check
```

---

## 14. License

License: MIT
