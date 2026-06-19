# Phase 0 Audit: `zotero-evidence-review/SKILL.md`

审计日期：2026-06-19  
审计对象：`zotero-evidence-review/SKILL.md`  
对应计划：`zotero-evidence-review/SKILL_IMPROVEMENT_PLAN.md` → Phase 0  
目标：判断当前 skill 是否已经支持高质量科研证据输出，并识别会影响 evidence review 输出质量的规则缺口。

---

## 1. 总体结论

当前 `zotero-evidence-review/SKILL.md` 已经具备较完整的 Zotero + PubMed 证据包工作流，尤其在以下方面基础较好：

- 有清晰的 intent routing；
- 能覆盖 Zotero semantic / keyword search；
- 能执行 paragraph claim extraction、citation placement、diff paragraph；
- 已将 PubMed 作为独立扩展层，而不是误当作 Zotero 功能；
- 已要求 PubMed 未执行、失败、完成三种状态不能混淆；
- 已有 Metadata QC 与 RIS 规则；
- 已有“不捏造 citation / metadata / RIS”的基本安全约束。

但从高质量科研证据输出角度看，当前 skill 仍存在 P0/P1 级规则缺口：

1. **没有强制区分 current-study finding 与 external literature evidence**。这会导致用户当前研究结果被外部文献错误“背书”。
2. **没有统一的 evidence level 体系**。目前只有 direct / indirect / mechanistic 等标签，缺少跨报告稳定的 A-E 证据等级。
3. **报告开头缺少 Status 与 Critical Warnings 前置区**。PubMed failed、citation unverified、no direct evidence 等风险虽然有时记录在后文，但不够醒目。
4. **Recommended Manuscript Text 没有拆分 copy-ready 与 annotated recommendation**。可能混入审查说明，降低直接复制到 manuscript 的可用性。
5. **RIS 生成前的 canonical reference gate 不够强制**。已有 metadata QC，但缺少每条 selected reference 的 canonical identifier、canonical key、duplicate decision 与 RIS action gate。
6. **Quality Gates 尚未系统检查 causal overclaim、BMI-independent overclaim、horizontal/direct pleiotropy overclaim**。
7. **Appendix template 不够机器可解析**。目前模板可读性强，但缺少固定 status 字段、warning table、evidence level、source layer、search reproducibility schema 等稳定列。

建议后续 Phase 1-9 按计划推进；若只做最小高影响修改，应优先修改 Module 2、Module 2.5、Markdown Report Requirements、Metadata QC、Quality Gates 与 `EVIDENCE_REVIEW_REPORT` 模板。

---

## 2. Phase 0 检查点逐项审计

| 检查点 | 当前覆盖情况 | 主要发现 | 风险等级 | 建议 |
|---|---|---|---|---|
| Intent Detection 是否覆盖中文科研用户常见输入 | 部分覆盖较好 | 已覆盖“使用技能”“完整工作流”“找证据”“找引文”“补引用”“推荐引用”“参考文献”“生成报告”“保存结果”“导出参考文献”等中文触发词 | 中 | 增补“润色并补引用”“讨论部分”“引言部分”“帮我证明/支持这句话”“审稿人会不会质疑”等科研写作口语输入 |
| Module 2 是否区分 direct / indirect / mechanistic / current-study finding | 部分覆盖 | 已有 direct、indirect、mechanistic、methodological、background、contrasting、gap；但没有 current-study finding/source layer | 高 | 增加 source layer，并强制标记 current-study / external evidence / interpretive bridge / unsupported gap |
| Module 2.5 是否有 package status 判断 | 缺失 | 没有 Ready / Caution / Partial / Superseded / Unknown 状态模型 | 高 | 在 Module 2.5 开头和 report metadata 中加入 Evidence Package Status |
| Markdown Report Requirements 是否有 copy-ready text | 部分覆盖 | 有“推荐稿件文本”，但没有明确 copy-ready；也没有 annotated text 分层 | 高 | 拆分为 Copy-ready Manuscript Text 与 Annotated Recommended Text |
| Metadata QC 是否强制 canonical reference | 部分覆盖 | 已检查 missing metadata、mismatch、duplicate、RIS standardization source；但缺少 canonical identifier/key 与 pre-RIS gate | 高 | 增加 Reference Canonicalization Gate，unresolved mismatch 不得进入 RIS |
| PubMed failed / not executed / completed 是否在报告前部可见 | 部分覆盖 | PubMed status 必须出现在 section 7，metadata 也有来源字段；但报告前部没有 Critical Warnings/status block | 高 | 在 report metadata 后立即加入 Critical Warnings 与 PubMed status summary |
| Quality Gates 是否检查 causal / BMI-independent / horizontal pleiotropy overclaim | 不足 | 只笼统要求谨慎因果措辞；未明确 BMI-independent 与 horizontal/direct pleiotropy 风险 | 高 | 在 Quality Gates 加入三类 overclaim 自检 |
| Appendix template 是否稳定、可机器解析 | 部分覆盖 | 有固定模板，但表头缺少 status、source layer、evidence level、critical warnings、search reproducibility | 中-高 | 更新 `EVIDENCE_REVIEW_REPORT`、`CLAIM_EVIDENCE_MATRIX` 与新增 reproducibility/QC gate 表 |

---

## 3. 已有优点

### 3.1 Intent Detection 基础较强

`SKILL.md` 的 intent routing 已能识别：

- `search`：关键词、概念、自然语言问题；
- `paragraph`：段落证据分析；
- `package`：保存报告、RIS、找证据、补引用、推荐引用等；
- `verify`：具体引用 + 具体 claim；
- `health`：库状态、索引状态、preflight。

对中文科研用户，当前已覆盖一批高频触发词：

- “使用技能”；
- “完整工作流”；
- “找证据”；
- “找引文”；
- “补引用”；
- “推荐引用”；
- “参考文献”；
- “文献引用”；
- “生成报告”；
- “保存结果”；
- “导出参考文献”。

这已经可以支持多数“我给一段文字，请帮我补引用并生成文件”的使用场景。

### 3.2 PubMed runtime status 规则比较清楚

已有规则明确指出：

- PubMed MCP 是 optional；
- 只有 PubMed-capable tool 可见且实际执行后，才能标记 `Completed`；
- 未执行要标记 `⚠️ Tool unavailable; search not executed` 或 `Not executed`；
- 搜索失败要标记 `Failed; query reported`；
- PubMed-only RIS 只能来自 completed PubMed search 且 metadata inspected。

这是非常重要的防幻觉机制。

### 3.3 Metadata QC 与 RIS 规则已有基础

当前已有：

- missing metadata 检查；
- Zotero / PubMed / DOI-derived metadata mismatch 检查；
- duplicate warning；
- RIS standardization source；
- unresolved metadata conflict 默认排除出 RIS；
- RIS file 必须是纯 RIS，不允许 Markdown heading/code fence。

这些规则已经为 Phase 7 的 canonical gate 打下基础。

### 3.4 中文报告与官方 metadata 分离较好

当前 Durable Output Language Policy 合理区分：

- 报告说明、warning、QC 用中文；
- manuscript 原语言保留；
- article title、journal、author、DOI、PMID 保留官方格式；
- RIS syntax 不本地化。

这对中文科研用户非常实用。

---

## 4. 缺失规则

### 4.1 缺少 current-study finding 与 external literature evidence 的强制边界

当前 Module 2 能标记 direct / indirect / mechanistic / methodological / background 等 evidence type，但这些标签主要描述“外部文献支持类型”，没有描述 claim 的来源层级。

缺失的关键字段：

- `Current study`；
- `Zotero external evidence`；
- `PubMed external evidence`；
- `Interpretive bridge`；
- `Unsupported gap`。

高风险场景：

- 用户写“我们的 SMR 分析发现 A 与 B 存在因果关联”；
- skill 找到外部文献说 A 与 B 有关联；
- 输出误写成“已有研究支持我们的因果发现”；
- 实际上外部文献只能支持 biological plausibility，不能验证当前研究的 SMR result。

尤其需要覆盖的 current-study finding 类型：

- GWAS / MR / SMR / TWAS / colocalization；
- MAGMA / LDSC / genetic correlation；
- mediation analysis；
- enrichment analysis；
- candidate gene prioritization；
- differential expression / single-cell enrichment；
- user-provided cohort result；
- manuscript 中以“本研究发现”“our analysis identified”描述的结果。

### 4.2 缺少统一 evidence level 体系

当前 evidence strength 表达包括：

- strong / direct；
- indirect；
- mechanistic；
- background；
- contrasting；
- gap；
- 支持 / 部分支持 / 缺口；
- 高 / 中 / 低 confidence。

问题是这些标签没有统一的层级定义，容易在不同报告中漂移。

建议统一为：

| Level | 名称 | 核心含义 |
|---|---|---|
| A | Exact direct support | 外部文献直接支持 exact claim |
| B | Close direct support | 直接支持相近 claim，但非完全相同 |
| C | Plausibility support | 机制、背景、review、pathway plausibility |
| D | Current-study only | 当前研究发现，外部文献只提供背景或合理性 |
| E | Unsupported / contradicted / verify | 未支持、相矛盾或需要验证 |

### 4.3 缺少报告开头 Status 与 Critical Warnings

当前 `EVIDENCE_REVIEW_REPORT` 的开头包括：

- title；
- date；
- source/PubMed status；
- input；
- Bottom Line。

但缺少两个关键前置块：

1. `Evidence Package Status`；
2. `Critical Warnings`。

这会导致：

- PubMed failed 的风险埋在后文 PubMed Expansion；
- no direct evidence 的风险埋在 matrix 或 reviewer-risk；
- citation unverified / metadata mismatch 不够醒目；
- 用户可能直接复制 Recommended Manuscript Text 而忽略风险。

### 4.4 Copy-ready 与 annotated recommendation 未分离

当前第 2 节是 `推荐稿件文本（Recommended Manuscript Text）`，第 8 节又有 `Integrated Writing Advice`。

问题：

- 没有明确第 2 节必须可直接复制进 manuscript；
- 没有禁止在该节写“需要核实 citation”“PubMed 未执行”“workflow 说明”；
- 证据解释可能混入推荐文本；
- 没有单独 annotated text 用于解释 citation rationale 和 caveats。

### 4.5 缺少 PubMed failed / citation unverified / no direct evidence 的前置风险提醒

虽然 PubMed status 有规范，但没有要求这些风险进入开头 Critical Warnings：

- PubMed tool unavailable；
- PubMed failed；
- citation/concept not verified；
- central claim has no direct evidence；
- no direct evidence only mechanistic plausibility；
- current-study finding could be mistaken as external evidence；
- metadata mismatch unresolved。

### 4.6 Search reproducibility schema 不统一

当前有 Zotero Search Summary 和 PubMed Expansion，但没有统一 schema 记录：

- source；
- query；
- mode；
- max_results；
- status；
- hits；
- included_count；
- full_text_inspected；
- excluded_reason；
- notes。

这会影响后续审计、复跑、项目级 summary 与结构化质量追踪。

### 4.7 Canonical reference gate 不够强制

当前 Metadata QC 有 QC table，但 RIS 生成前缺少明确 gate：

每篇 selected reference 应强制记录：

- canonical identifier；
- canonical Zotero key；
- duplicate keys；
- metadata source of truth；
- mismatch status；
- RIS action；
- reason。

目前的 `RIS action` 允许 `Include / exclude / needs manual check`，建议标准化为：

- `Include`；
- `Exclude`；
- `Verify`；
- `Optional`。

### 4.8 QA self-audit 不足

当前 Quality Gates 检查文件存在、RIS 纯净、PubMed-only 规则、metadata warning，但没有系统检查科研推断过度。

必须新增：

- causal overclaim；
- association-as-causation；
- BMI-independent overclaim；
- horizontal/direct pleiotropy overclaim；
- genetic colocalization / MR / SMR 过度外推；
- mechanistic plausibility 被写成 direct evidence；
- current-study finding 被 external evidence “证明”。

---

## 5. 高优先级改进

### P0：立即改

1. **Evidence Package Status**
   - 在 Module 2.5 与 `EVIDENCE_REVIEW_REPORT` 开头加入 `Ready / Caution / Partial / Superseded / Unknown`。

2. **Critical Warnings 前置**
   - 在 Metadata 后、Bottom Line 前加入 warning table。
   - Final chat summary 也显示 status 和 critical warnings。

3. **Evidence Level A-E**
   - 所有 claim 使用统一 evidence level。
   - `D = Current-study only`，防止外部文献错误背书当前发现。

4. **Source Layer**
   - Claim–Evidence Matrix 增加 `Source layer`。
   - 强制区分 current study、Zotero external evidence、PubMed external evidence、interpretive bridge、unsupported gap。

5. **Copy-ready / Annotated 双层输出**
   - Copy-ready text 不允许混入 QC/warning/workflow 说明。
   - Annotated text 解释 citation rationale 和 caveats。

### P1：强烈建议改

1. **Search Reproducibility schema**
   - 统一 Zotero/PubMed 检索日志表。

2. **Reference Canonicalization Gate**
   - RIS 前强制 canonical identifier/key/source/action。

3. **Overclaim QA Gate**
   - 写文件前执行 QA self-audit。

4. **Appendix templates 稳定化**
   - 更新 `CLAIM_EVIDENCE_MATRIX`、`EVIDENCE_REVIEW_REPORT`、Metadata QC 表头。

---

## 6. 建议插入到 `SKILL.md` 的位置

| 插入位置 | 建议新增内容 |
|---|---|
| `## 0. Intent Detection` → Routing Rules 后 | 增补中文科研写作触发词与“审稿风险/补引用/润色讨论”等口语输入 |
| `## 2. Paragraph Evidence & Citation Analysis` → `### Core Principle` 后 | 新增 `Current-study vs External Evidence Boundary` |
| `## 2. Paragraph Evidence & Citation Analysis` → `### Evidence and Rationale Labels` 前/后 | 新增 `Evidence Level A-E` 与 `Source Layer` |
| `## 2.5 Evidence Package Export` → `### Workflow` 前 | 新增 `Evidence Package Status` |
| `### Markdown Report Requirements` | 更新 section 顺序，加入 Metadata + Status、Critical Warnings、Copy-ready、Annotated、Search Reproducibility |
| `### Metadata Quality Control` 前 | 新增 `Reference Canonicalization Gate` |
| `### Quality Gates` | 加入 QA self-audit 与 overclaim checks |
| `Appendix: Output Templates → CLAIM_EVIDENCE_MATRIX` | 更新表头，加入 source layer/evidence level |
| `Appendix: Output Templates → EVIDENCE_REVIEW_REPORT` | 更新完整模板 |
| `### Output Format` | Final chat summary 加入 Status 与 Critical Warnings |

---

## 7. 可直接复制进 `SKILL.md` 的规则草案

以下规则草案可作为 Phase 1-9 的落地素材。

---

### 7.1 Intent Detection 增强草案

建议插入位置：`## 0. Intent Detection` → `### Routing Rules` 后。

```markdown
### Chinese Scientific-writing Trigger Expansion

For Chinese research users, also treat the following as `package` or paragraph citation-support triggers when attached to a manuscript paragraph, draft section, claim, or topic:

- `帮我润色并补引用`
- `讨论部分怎么写`
- `引言部分找证据`
- `这句话需要什么文献支持`
- `帮我证明这句话`
- `帮我找支撑这句话的文献`
- `审稿人会不会质疑`
- `这段话证据够不够`
- `帮我降低因果表述风险`
- `补充机制证据`
- `找直接证据`
- `找间接证据`
- `找审稿风险`
- `生成可复制到论文里的文本`

If the request asks for manuscript-ready wording, citation placement, reviewer-risk assessment, or reusable files, default to the full Paragraph Citation Package Workflow unless the user explicitly opts out of file generation.
```

---

### 7.2 Current-study vs External Evidence Boundary 草案

建议插入位置：`## 2. Paragraph Evidence & Citation Analysis` → `### Core Principle` 后。

```markdown
### Current-study vs External Evidence Boundary

Every extracted claim must be assigned a `Source layer` before evidence is interpreted. This boundary prevents external literature from being used to over-validate the user's own study findings.

Allowed `Source layer` values:

| Source layer | Definition | Typical wording |
|---|---|---|
| `Current study` | A finding produced by the user's current manuscript, dataset, analysis, or supplied results. | `In our analysis...`, `The present study identified...`, `Our results suggest...` |
| `Zotero external evidence` | Evidence from inspected Zotero records. | `Previous studies show...`, `Published evidence supports...` |
| `PubMed external evidence` | Evidence from PubMed records whose metadata was inspected after a completed PubMed search. | `PubMed-indexed studies report...` |
| `Interpretive bridge` | A cautious synthesis connecting current-study findings with external evidence. | `These findings are consistent with...`, `may suggest...`, `support biological plausibility...` |
| `Unsupported gap` | A claim for which no adequate direct, indirect, or mechanistic evidence was found. | `requires validation`, `was not directly supported by retrieved evidence` |

Claims involving the following must normally be marked as `Current study` unless the user explicitly says they come from a cited external paper:

- GWAS, MR, SMR, TWAS, colocalization, fine-mapping, genetic correlation, LDSC, MAGMA;
- mediation analysis, enrichment analysis, pathway enrichment, cell-type enrichment;
- candidate gene prioritization, differential expression, single-cell analysis;
- user cohort results, original statistical models, tables, figures, supplementary results;
- wording such as `本研究发现`, `我们的研究发现`, `our analysis identified`, `we found`, `the present study shows`.

External literature may support background, prior association, mechanism, biological plausibility, or methodological rationale. It must not be described as proving, confirming, validating, or independently reproducing a current-study finding unless the retrieved external evidence directly tests the same claim with comparable design, exposure, outcome, and population.

Forbidden wording when only external plausibility evidence is available:

- `This proves our finding`
- `Previous studies confirmed our causal result`
- `External evidence validates our SMR/MR/TWAS result`
- `The mechanism was established by our citation` when the citation only provides background or indirect evidence

Preferred cautious wording:

- `Our finding is consistent with previous evidence that...`
- `Published studies provide biological plausibility for...`
- `These results should be interpreted as hypothesis-generating pending direct validation.`
```

---

### 7.3 Evidence Level A-E 草案

建议插入位置：`## 2. Paragraph Evidence & Citation Analysis` → `### Evidence and Rationale Labels` 前。

```markdown
### Unified Evidence Level

Assign every claim one evidence level from A to E. Use the same level in chat output, Markdown evidence reports, reviewer-risk assessment, and recommended wording.

| Level | Name | Definition | Recommended wording | Avoid |
|---|---|---|---|---|
| `A` | Exact direct support | External literature directly supports the exact claim with matching exposure/intervention, outcome, direction, and study context. | `directly supported`, `shown to be associated with`, `reported to reduce/increase` when design supports it | Adding extra causal or population claims not in the source |
| `B` | Close direct support | External literature directly supports a closely related claim, but one element differs, such as population, phenotype, exposure, or method. | `consistent with`, `supports a related association`, `aligns with evidence from...` | `proves`, `confirms the exact claim` |
| `C` | Plausibility support | Evidence is mechanistic, pathway-level, review-based, background, or indirect. | `biologically plausible`, `may be linked to`, `could contribute to`, `provides mechanistic context` | Treating mechanism/background as direct empirical support |
| `D` | Current-study only | The claim is mainly from the user's current analysis; external literature only gives context or plausibility. | `In our analysis`, `our findings suggest`, `this observation is consistent with...` | `previous studies confirmed our finding` unless direct replication exists |
| `E` | Unsupported / contradicted / verify | No adequate evidence found, evidence contradicts the claim, or citation/metadata requires verification. | `requires validation`, `should be removed or hedged`, `not directly supported by retrieved evidence` | Presenting as established fact |

Rules:

- `D` must be used for user-generated results even if external mechanistic literature exists.
- `C` must not be upgraded to `A` or `B` unless direct empirical evidence for the same claim is retrieved.
- `E` claims must not appear in copy-ready manuscript text as confident factual statements.
- The `Evidence level` should drive hedging: A/B can use moderate confidence; C/D require cautious wording; E requires removal, verification, or strong hedge.
```

---

### 7.4 Evidence Package Status 草案

建议插入位置：`## 2.5 Evidence Package Export` → `### Workflow` 前。

```markdown
### Evidence Package Status

Every generated evidence package must receive exactly one status: `Ready`, `Caution`, `Partial`, `Superseded`, or `Unknown`.

| Status | Definition | User guidance |
|---|---|---|
| `Ready` | Searches completed as planned, central claims have adequate direct or close support, metadata QC found no unresolved high-risk issue, and RIS records passed canonical checks. | Suitable for manuscript drafting with normal scholarly caution. |
| `Caution` | The package is usable but has important caveats, such as indirect evidence, no direct evidence for a central claim, duplicate warnings safely handled, or cautious wording required. | Use only with hedge wording and review the warnings. |
| `Partial` | A required evidence layer failed or was unavailable, key citations/concepts were not verified, PubMed failed for a biomedical topic, or metadata conflicts remain unresolved. | Do not treat as final; complete missing verification before submission. |
| `Superseded` | A later package or updated run replaces this one. | Keep for history only; cite/use the newer package. |
| `Unknown` | Status cannot be determined from available tool results or report content. | Manual review required. |

Downgrade triggers:

- PubMed unavailable for a biomedical package → at least `Caution`; use `Partial` if PubMed evidence was required for central claims.
- PubMed search failed after being attempted → at least `Partial` unless PubMed was nonessential and Zotero direct evidence is sufficient.
- Central claim has no direct evidence → at least `Caution`.
- Citation or key concept not verified → at least `Caution`; use `Partial` if it affects a central claim.
- Unresolved metadata mismatch in selected references → `Partial`; exclude the affected reference from RIS.
- Current-study finding could be mistaken for external evidence → at least `Caution` until wording is fixed.
- No direct evidence and only mechanistic plausibility for a causal claim → at least `Caution`.
- All required evidence inspected and risks low → `Ready`.
```

---

### 7.5 Critical Warnings 前置草案

建议插入位置：`### Markdown Report Requirements` 与 `EVIDENCE_REVIEW_REPORT` 开头。

```markdown
### Critical Warnings Requirement

Every Markdown evidence report must include `Critical Warnings` immediately after metadata/status and before the bottom-line conclusion.

Add a warning when any of the following occurs:

- PubMed tool unavailable, PubMed search not executed, or PubMed search failed;
- central claim has no direct evidence;
- external evidence contradicts or weakens a draft claim;
- citation, PMID, DOI, title, or key concept is unverified;
- metadata mismatch remains unresolved;
- duplicate Zotero/PubMed records affect selected references;
- a current-study finding could be mistaken for external literature evidence;
- causal wording is not supported by study design or evidence level;
- BMI-independent wording is not directly supported;
- horizontal pleiotropy, direct pleiotropy, or shared causal variant wording is not directly supported.

Format:

| Warning ID | Affected claim | Risk | Required action |
|---|---|---|---|
| W1 | ... | PubMed failed / no direct evidence / overclaim / metadata mismatch | Re-run search / hedge wording / remove claim / verify citation |

If no warnings are present, write: `No critical warnings.`

The final chat summary must also include the package status and critical warnings. Do not bury critical warnings only in later sections.
```

---

### 7.6 Copy-ready 与 Annotated 双层输出草案

建议插入位置：`### Markdown Report Requirements` 与 `EVIDENCE_REVIEW_REPORT`。

```markdown
### Copy-ready vs Annotated Recommendation

Separate manuscript-ready text from evidence annotations.

`Copy-ready Manuscript Text` rules:

- Must be directly copyable into a manuscript.
- Preserve the manuscript's original language unless translation is requested.
- Do not include workflow notes, QC notes, internal reasoning, `citation should be verified`, PubMed status explanations, or Markdown warning labels inside the prose.
- Use hedge wording when evidence level is B, C, D, or E.
- Do not present unsupported or unverified concepts as established facts.
- Do not include E-level claims as confident statements.

`Annotated Recommended Text` rules:

- May explain citation placement, evidence level, source layer, caveats, and reviewer-risk rationale.
- Must identify which parts are current-study findings and which are external evidence.
- Must explain when a citation supports background, mechanism, method, direct evidence, or plausibility only.

Required sections:

```markdown
## Copy-ready Manuscript Text
> {text that can be copied directly into the manuscript}

## Annotated Recommended Text
| Sentence / clause | Text | Source layer | Evidence level | Citation rationale | Caveat |
|---|---|---|---|---|---|
```
```

---

### 7.7 Search Reproducibility Schema 草案

建议插入位置：`### Markdown Report Requirements` 与 `EVIDENCE_REVIEW_REPORT` 的 PubMed/Zotero search sections 后。

```markdown
### Search Reproducibility

Every evidence package must include a reproducibility table covering Zotero and PubMed searches, including failed or unavailable searches.

| Source | Query | Mode | Max results | Status | Hits | Included | Full text inspected | Excluded / reason | Notes |
|---|---|---|---:|---|---:|---:|---|---|---|
| Zotero | ... | semantic / keyword / collection / tag | ... | Completed / Failed / Not executed | ... | ... | yes / no / partial | ... | ... |
| PubMed | ... | Boolean / MeSH / related | ... | Completed / ⚠️ Tool unavailable; search not executed / Failed; query reported / Not executed | ... | ... | yes / no / partial | ... | ... |

Rules:

- Record the exact Zotero semantic query when available.
- Record the exact keyword/structured fallback query when used.
- Record the exact PubMed query even when PubMed was unavailable or failed.
- Mark PubMed `Completed` only when the search actually ran and selected PMID metadata was inspected.
- Record included PMIDs and excluded records/reasons when PubMed results are screened.
- Do not claim full text was inspected unless Zotero/PubMed full text, PDF pages, or equivalent text was actually read.
```

---

### 7.8 Reference Canonicalization Gate 草案

建议插入位置：`### Metadata Quality Control` 前。

```markdown
### Reference Canonicalization Gate

Before writing RIS records, every selected reference must pass a canonicalization gate.

For each selected reference, inspect and record:

- DOI;
- PMID;
- title;
- first author;
- year;
- journal / publication title;
- Zotero item key when applicable;
- PubMed PMID when applicable;
- duplicate candidate keys or PMIDs;
- metadata source of truth;
- final RIS action.

Canonicalization table:

| Citation | Canonical identifier | Canonical Zotero key | Duplicate keys / PMIDs | Metadata source of truth | Mismatch status | RIS action | Reason |
|---|---|---|---|---|---|---|---|
| Author Year | DOI / PMID / Zotero key | KEY / — | KEY2; PMID... / none | PMID/PubMed / DOI / Zotero metadata / PubMed metadata | none / possible mismatch / unresolved | Include / Exclude / Verify / Optional | ... |

Rules:

- If DOI or PMID is identical across records, treat them as the same candidate reference and choose one canonical record.
- If multiple Zotero keys represent the same article, select one canonical Zotero key and list duplicate keys.
- If Zotero and PubMed metadata conflict on DOI, PMID, normalized title, first author, year, or journal, mark `Possible metadata mismatch`.
- `RIS action` must be one of `Include`, `Exclude`, `Verify`, or `Optional`.
- Unresolved metadata mismatch must not enter RIS.
- PubMed-only records may enter RIS only when PubMed search status is `Completed` and selected PMID metadata was inspected.
```

---

### 7.9 QA Self-audit 与 overclaim gate 草案

建议插入位置：`### Quality Gates`。

```markdown
### QA Self-audit Before Writing Files

Before writing the Markdown report and RIS file, perform an internal self-audit. If any check fails, fix the report before claiming completion.

Required checks:

- Report contains `Evidence Package Status`.
- Report contains `Critical Warnings` or `No critical warnings`.
- Report contains `Copy-ready Manuscript Text` and `Annotated Recommended Text` as separate sections.
- Claim–Evidence Matrix contains `Source layer` and `Evidence level`.
- Current-study findings are not written as if external literature proved them.
- PubMed status accurately reflects actual tool execution: `Completed`, `⚠️ Tool unavailable; search not executed`, `Failed; query reported`, or `Not executed`.
- PubMed-only RIS records are included only after completed PubMed search and inspected metadata.
- Metadata QC includes canonical identifier, mismatch status, duplicate status, and RIS action.
- RIS file contains RIS records only, with no Markdown headings, comments, explanations, or code fences.
- Paths in final chat output are relative paths.

Overclaim checks:

- Do not write association evidence as causal evidence.
- Do not write mechanistic plausibility as direct empirical support.
- Do not claim BMI-independent effects unless retrieved evidence directly adjusts for BMI or explicitly tests BMI independence.
- Do not claim horizontal pleiotropy, direct pleiotropy, shared causal variants, or colocalized causal mechanisms unless direct genetic evidence supports that exact statement.
- Do not claim MR/SMR/TWAS/colocalization results are externally validated unless an independent comparable study directly replicated the same result.
- E-level claims must be removed, converted to a knowledge gap, or heavily hedged.

Final chat output should expose only:

- package status;
- Markdown path;
- RIS path;
- critical warnings.
```

---

### 7.10 Updated Claim–Evidence Matrix 模板草案

建议替换：`Appendix: Output Templates → CLAIM_EVIDENCE_MATRIX`。

```markdown
### CLAIM_EVIDENCE_MATRIX

```markdown
| # | Claim | Source layer | Evidence level | Zotero evidence | PubMed evidence | Evidence status | Confidence | Risk | Recommended action | Recommended citation |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | X is associated with Y | Zotero external evidence | A | Author 2022 (KEY) | PMID confirms | Supported | High | Low | Cite directly | Author 2022 |
| 2 | Our analysis identified Z as causal for W | Current study | D | Mechanistic background only | No direct evidence | Current-study only | Medium | Causal overclaim | Hedge and separate current result from external plausibility | Author 2023 for mechanism only |
| 3 | A directly causes B independent of BMI | Unsupported gap | E | — | — | Unsupported | Low | BMI-independent overclaim | Remove or verify | — |
```

Rules:

- One row per extracted claim.
- `Source layer` must use: `Current study`, `Zotero external evidence`, `PubMed external evidence`, `Interpretive bridge`, or `Unsupported gap`.
- `Evidence level` must use A, B, C, D, or E.
- Current-study findings must not be upgraded to external direct evidence merely because related literature exists.
- Evidence level C or D requires hedge wording.
- Evidence level E requires removal, verification, or explicit knowledge-gap framing.
```

---

### 7.11 Updated `EVIDENCE_REVIEW_REPORT` section order 草案

建议替换：`### Markdown Report Requirements` 的 section list，并同步更新 Appendix template。

```markdown
The Markdown evidence report must include these sections in order:

1. `Metadata and Use Status`
2. `Critical Warnings`
3. `核心结论（Bottom Line）`
4. `Copy-ready Manuscript Text`
5. `Annotated Recommended Text`
6. `主张—证据矩阵（Claim–Evidence Matrix）`
7. `引文放置建议（Citation Placement）`
8. `参考文献表（Reference Table）`
9. `Search Reproducibility`
10. `Zotero 检索总结（Zotero Search Summary）`
11. `PubMed 扩展检索（PubMed Expansion）`
12. `综合写作建议（Integrated Writing Advice）`
13. `Claims to Revise or Remove`
14. `证据缺口与审稿风险（Gaps and Reviewer-risk Assessment）`
15. `Reference Canonicalization Gate`
16. `元数据质量控制（Metadata Quality Control）`
17. `导出文件（Export File）`
```

---

### 7.12 Final chat output 草案

建议替换：`## 2.5 Evidence Package Export` → `### Output Format`。

```markdown
In chat, after files are written, output only:

```markdown
Generated Evidence Package:
- Status: Ready / Caution / Partial / Superseded / Unknown
- Markdown report: `zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_evidence_review.md`
- EndNote RIS: `zotero-evidence-output/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}/{brief_topic_slug}_{YYYY-MM-DD_HHMMSS}_references.ris`

Critical Warnings:
- No critical warnings.
```

If warnings exist:

```markdown
Critical Warnings:
- W1: PubMed search failed; central claim relies on Zotero-only evidence. Required action: rerun PubMed or use hedge wording.
- W2: No direct evidence for BMI-independent claim. Required action: remove `BMI-independent` or verify with direct evidence.
```

Do not include full report content in final chat after files are written.
```

---

## 8. 推荐执行顺序

建议下一阶段按以下顺序落地：

1. Phase 1：先加入 `Evidence Package Status`；
2. Phase 2：加入 Evidence Level A-E；
3. Phase 3：加入 Source Layer/current-study boundary；
4. Phase 5：加入 Critical Warnings 前置；
5. Phase 4：拆分 Copy-ready 与 Annotated；
6. Phase 7：加入 Reference Canonicalization Gate；
7. Phase 6：加入 Search Reproducibility；
8. Phase 9：加入 QA Self-audit；
9. Phase 10：统一更新 Appendix templates。

如果只做最小可行修改，优先将以下 4 块复制进 `SKILL.md`：

1. `Evidence Package Status`；
2. `Current-study vs External Evidence Boundary` + `Evidence Level A-E`；
3. `Critical Warnings Requirement` + `Copy-ready vs Annotated Recommendation`；
4. `QA Self-audit Before Writing Files`。

---

## 9. Phase 0 完成标记

Phase 0 审计已完成。当前 `SKILL.md` 的主要能力与缺口已经明确，后续可直接进入 Phase 1-3 的规则落地开发。
