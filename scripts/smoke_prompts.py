#!/usr/bin/env python3
"""Print safe manual smoke-test prompts for Zotero/PubMed MCP workflows."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class SmokePrompt:
    key: str
    title: str
    text: str


COMMON_GUARDRAIL = """只读测试；不要修改 Zotero；不要生成文件；不要创建、更新或删除任何 note/annotation/item。\n如果相关 MCP tool 在当前会话不可见，请明确写 unavailable，不要假装已检索。\n不要伪造 PMID、DOI、RIS 或 citation。\n不要把 `Tool skipped because a previous tool call in the scheduled sequence failed` 当作已执行；如果出现该错误，请报告同一调度序列中的第一个失败工具。\n搜索/status 与 metadata/details/fulltext 等下游调用必须分步进行：先执行上游 tool，检查结果后再决定是否单独调用下游 tool，不要同批调度依赖调用。"""

PROMPTS = [
    SmokePrompt(
        "zotero-literature-learning-dry-run",
        "Zotero literature learning materials pipeline dry run",
        f"""/zotero-literature-learning 只读路由验证，不要生成文件：如果用户要求“先从 Zotero 找 3–5 篇同领域论文，读取摘要/全文，学习 Introduction、Methods 或 Results 的写法，然后再改稿”，请说明应按 Stage 0–8 执行：先建立 task_contract；再按 zotero_get_recent → zotero_semantic_search → zotero_search_items/advanced_search → zotero_get_item_metadata → zotero_get_item_children → zotero_get_pdf_outline → zotero_read_pdf_pages（必要时 zotero_get_item_fulltext fallback）分步调用；建立 corpus ledger、reading queue、Evidence/Style/Argument Profile 和 handoff。只能抽象模式，不复制同行原句；默认不生成 RIS；全文/工具不可用时标记 corpus_status: unavailable 或 Caution，不得伪造结果。\n{COMMON_GUARDRAIL}\n请只输出预期阶段、状态字段、停止条件和下游 handoff，不要实际检索或写文件。""",
    ),
    SmokePrompt(
        "zotero-writing-block-learning-dry-run",
        "Zotero writing-block learning and methods wording dry run",
        f"""/zotero-literature-learning 只读路由验证，不要生成文件：用户知道研究内容但觉得 Methods overview 太啰嗦，并怀疑“gene-, tissue-, and pathway-level annotation”中的 annotation 不准确。请先建立 writing_block_type=method_naming/wording 和 must_preserve 清单，再按 Zotero MCP 分步寻找同领域、同章节、同文章类型的 3–5 篇高匹配片段；比较 subject–verb 结构、方法术语、并列分析动作和证据边界；输出 WRITING_BLOCK_LEARNING、2–3 个保守候选版本、annotation/analysis/characterization/enrichment 的术语决策、author checks。若目标是 Introduction 或其他引用驱动段落，必须先建立 evidence map、paragraph blueprint 和 evidence coverage；不得复制同行原句或改变研究设计、数字和 claim strength。\n{COMMON_GUARDRAIL}\n请只输出预期流程和字段，不要实际检索或写文件。""",
    ),
    SmokePrompt(
        "zotero-manuscript-thinking-dry-run",
        "Zotero manuscript-level thinking route dry run",
        f"""/zotero-evidence-review 只读路由验证，不要生成文件：如果用户提供标题、摘要、Introduction、Results 和 Discussion，并要求“从全文角度看看语言精确度、Introduction/Discussion 逻辑、论文主线和下一轮修改顺序”，请说明应路由到 Module 2.8 Manuscript-Level Thinking Checkpoint 和 companion zotero-manuscript-thinking Skill。\n{COMMON_GUARDRAIL}\n请只输出 scope ledger、paper contract、Language Audit、Introduction/Discussion Logic Map、argument spine、thinking-model-router 的 primary route、P0/P1 action table、下游 handoff 和 stop conditions；不要改写论文，不要承诺新实验。""",
    ),
    SmokePrompt(
        "zotero-domain-style-calibration-dry-run",
        "Zotero domain-native style calibration route dry run",
        f"""/zotero-manuscript-thinking 只读路由验证，不要生成文件：如果用户要求“参考 Zotero 中 3–5 篇同领域、同文章类型的代表性论文，检查 Introduction 的语言是否地道，并给出保守的 copy-ready 改写”，请说明应先建立 style_corpus_ledger，再按 zotero_get_recent → zotero_semantic_search → inspect → zotero_get_item_metadata → zotero_get_item_children → zotero_get_pdf_outline → zotero_read_pdf_pages 的顺序读取；然后输出 Domain Style Calibration、Zotero Style Evidence Ledger、peer pattern、calibration_confidence 和 draft-to-profile comparison；不得复制 peer 原文，不得改变 claim 强度。\n{COMMON_GUARDRAIL}\n如果 Zotero/PubMed MCP 不可见，请写 corpus_status: unavailable，并说明只能做 genre-neutral 语言诊断。不要实际检索或写文件。""",
    ),
    SmokePrompt(
        "zotero-methods-results-calibration-dry-run",
        "Zotero Methods/Results calibration route dry run",
        f"""/zotero-manuscript-thinking 只读路由验证，不要生成文件：如果用户要求“参考 Zotero 中同领域、同研究设计的论文，检查 Methods 是否可复现、Results 是否地道且叙事清楚，并核对 Methods–Results–图表一致性”，请说明应先建立按 section 分层的 style_corpus_ledger，再对 Methods 和 Results 分别抽取 reproducibility detail order、报告规范、结果块顺序、quantitative anchor、figure/table linking 和 interpretation boundary；然后输出 Methods Logic Map、Results Logic Map、Zotero Style Evidence Ledger、Methods–Results alignment audit 和 calibration_confidence。不得补写未提供的参数、改变数字/方向/单位或把 Results 解释成 Discussion。\n{COMMON_GUARDRAIL}\n如果 Zotero/PubMed MCP 不可见，请写 corpus_status: unavailable，并说明只能做 genre-neutral、evidence-bound 的章节诊断。不要实际检索或写文件。""",
    ),
    SmokePrompt(
        "zotero-fidelity-first-conflict-dry-run",
        "Zotero fidelity-first conflict rejection dry run",
        f"""/zotero-literature-learning 只读路由验证，不要生成文件：如果目标期刊论文反复使用某种写作模式，但该模式会改变当前研究的含义（例如把观察性关联写成因果、把有限样本的探索性结果写成普遍结论、或把同行论文的机制解释迁移到当前研究），请明确拒绝迁移该模式。先建立 Fidelity-First Contract：当前研究的设计、数据、结果、贡献、限制和 claim strength 是事实来源；目标期刊语料只能用于观察 reader path、paragraph function、information order、claim calibration、terminology 和 transition。逐条输出 peer pattern、current reader problem、transfer_scope（preserve/adapt/author_decide/reject_transfer）、拒绝理由、safe alternative 和 author_check；不得用“更像目标期刊”作为保留理由，也不得复制同行原句或结果。\n{COMMON_GUARDRAIL}\n请只输出预期阶段、fidelity gate、revision card 字段和停止条件，不要实际检索或写文件。""",
    ),
    SmokePrompt(
        "zotero-manuscript-mapping-revision-cards-dry-run",
        "Zotero complete manuscript mapping and revision cards dry run",
        f"""/zotero-literature-learning 只读路由验证，不要生成文件：如果用户提供一篇完整手稿和指定 Zotero 目标期刊语料，要求先学习论文的论证与读者路径，再给出写作改进建议，请说明应按 section/paragraph/sentence 建立稳定的 draft_segment_id，并逐段记录 rhetorical_job、target_reader_question、main_claim、evidence_anchor、information_order、claim_strength 和 reader_blocker。先输出 Manuscript Reader-path Map，再输出按 P0/P1/P2 排序的 Revision Cards；每张卡必须含 before、最多三个候选 after、recommended_writing_action、reasoning_gain、source_pattern_ids、transfer_scope、claim_delta、evidence_level、risk、author_check 和 selection_status: pending。先修论证架构、段落功能和信息顺序，再修术语和句子；不得自动选择最终版本、不得修改 Word/PDF/TeX/Zotero，也不得补写未提供的研究事实。\n{COMMON_GUARDRAIL}\n请只输出预期工作流、字段契约、fidelity checks 和 handoff，不要实际检索或写文件。""",
    ),
    SmokePrompt(
        "zotero-insufficient-corpus-genre-neutral-dry-run",
        "Zotero insufficient corpus genre-neutral fallback dry run",
        f"""/zotero-literature-learning 只读路由验证，不要生成文件：如果用户指定的 Zotero Collection 中目标期刊全文少于最低匹配数量，或只能读取摘要/元数据，必须降级为 genre-neutral 写作诊断，不能把一两篇论文的个人习惯描述成目标期刊规范。请记录 corpus_status、calibration_confidence、exact-match count、full-text coverage、inspected sections、unresolved gaps 和 recommendation_scope；只允许输出有证据支持的 reader-path、paragraph-function、claim-calibration 或 wording-if-reasoning 建议，并明确哪些判断不能做。若语料不足但当前手稿可读，仍可基于当前研究内容给出保守写作建议，但不得声称已完成目标期刊校准；若真正问题是证据缺口，应停止语言替换并转为 author_check/evidence_gap。\n{COMMON_GUARDRAIL}\n请只输出降级规则、状态字段、允许/禁止的建议范围和 handoff，不要实际检索或写文件。""",
    ),
    SmokePrompt(
        "zotero-health",
        "Zotero read-only health check",
        f"""/zotero-evidence-review 做一次 Zotero MCP 只读健康检查。\n{COMMON_GUARDRAIL}\n请只报告：当前会话是否能看到 Zotero MCP tools、语义索引/全文能力是否可检查、最近文献/collection/tag 检索是否能安全执行。""",
    ),
    SmokePrompt(
        "zotero-search",
        "Zotero chat-only evidence search",
        f"""/zotero-evidence-review 只在聊天输出，不要生成文件：检索 Zotero 本地库中关于 PCOS sedentary behavior cardiometabolic risk 的相关文献，最多列 5 篇，并说明每篇适合支持什么 claim。\n{COMMON_GUARDRAIL}\n先单独执行 Zotero search；检查返回结果后，再决定是否需要 metadata/fulltext。""",
    ),
    SmokePrompt(
        "zotero-search-export-dry-run",
        "Zotero ordinary search auto-export route dry run",
        f"""/zotero-evidence-review 只读路由验证，不要生成文件：如果用户请求“搜 Zotero 库中关于肠道菌群和抑郁症的文献”，请说明当前默认应先 Zotero semantic/keyword search，再在 PubMed MCP 可见时自动 PubMed expansion，最后生成 Search Report + RIS。\n{COMMON_GUARDRAIL}\n请只输出预期路由、Dual-MCP Auto Search and Export Defaults、Search Report + RIS 输出类型、PubMed unavailable 时的状态、以及预期相对路径格式 `zotero-evidence-output/{{brief_topic_slug}}_{{YYYY-MM-DD_HHMMSS}}/{{brief_topic_slug}}_{{YYYY-MM-DD_HHMMSS}}_literature_search.md` 和 `_references.ris`；不要实际写入 Markdown/RIS。""",
    ),
    SmokePrompt(
        "zotero-target-search",
        "Zotero target literature search",
        f"""/zotero-evidence-review 只在聊天输出，不要生成文件：哪些文献使用了大脑相关 GWAS 数据？最多列 8 篇。\n{COMMON_GUARDRAIL}\n请按 target_literature_search 处理：先做 topic decomposition，再给出 semantic query、keyword query、exact phrase query、noise-control concepts；结果必须分成 Core / Strong Related / Method Background / Disease GWAS Only / Noise / Verify，并为排除项写 Exclusion reason code。先单独执行 Zotero search；检查返回结果后，再决定是否需要 metadata/fulltext。""",
    ),
    SmokePrompt(
        "zotero-target-export-dry-run",
        "Zotero target search export route dry run",
        f"""/zotero-evidence-review 只读路由验证，不要生成文件：如果用户请求“哪些文献使用了大脑相关 GWAS 数据？”，请说明当前默认应走 target_literature_search 的 Search Report + RIS，而不是 Paragraph Citation Package Workflow，并在 PubMed MCP 可见时自动 PubMed expansion。\n{COMMON_GUARDRAIL}\n请只输出预期路由、Topic Decomposition、Query Expansion Plan、分类与排除原因表结构、Search RIS 纳入规则、PubMed unavailable 时的状态、以及预期相对路径格式 `zotero-evidence-output/{{brief_topic_slug}}_{{YYYY-MM-DD_HHMMSS}}/{{brief_topic_slug}}_{{YYYY-MM-DD_HHMMSS}}_literature_search.md` 和 `_references.ris`；不要实际写入 Markdown/RIS。""",
    ),
    SmokePrompt(
        "zotero-paragraph-package-export-dry-run",
        "Zotero paragraph polish/citation package route dry run",
        f"""/zotero-evidence-review 只读路由验证，不要生成文件：如果用户请求“帮我给这段话补引用并润色：慢性炎症通过激活 JAK-STAT 信号通路促进动脉粥样硬化斑块形成，而 IL-6 受体阻断剂可显著降低心血管事件风险。”，请说明应走 Paragraph Citation Package Workflow，默认生成 EVIDENCE_REVIEW_REPORT + Citation RIS。\n{COMMON_GUARDRAIL}\n请只输出预期路由、claim extraction、Zotero-first search、PubMed expansion、Citation Support Ledger、Copy-ready Manuscript Text、diff paragraph、Citation RIS 纳入规则、以及预期相对路径格式 `zotero-evidence-output/{{brief_topic_slug}}_{{YYYY-MM-DD_HHMMSS}}/{{brief_topic_slug}}_{{YYYY-MM-DD_HHMMSS}}_evidence_review.md` 和 `_references.ris`；不要实际写入 Markdown/RIS。""",
    ),
    SmokePrompt(
        "zotero-direct-paragraph-citation",
        "Zotero direct paragraph citation request",
        f"""/zotero-evidence-review 帮我找到这个段落每句话合适的引文，并生成可导入 EndNote 的 RIS：慢性炎症可能通过激活 JAK-STAT 信号通路促进动脉粥样硬化斑块形成。IL-6 受体阻断剂与较低的心血管事件风险相关。\n{COMMON_GUARDRAIL}\n请验证零配置入口：不要要求用户先拆句、提供 claim ID、选择模块或编写检索词；保留段落原文语义，自动建立 sentence_id 和 claim_id，按 Zotero semantic search、Zotero structured search、PubMed broad search、PubMed design/method search 分步检索；逐句输出 citation_need、证据等级、support verdict、evidence location、author check 和 RIS action。请说明每条推荐引文必须经过 metadata/abstract/full-text inspection，搜索摘要片段不能单独作为证据；输出 SENTENCE_CITATION_MATRIX、CITATION_COVERAGE_SUMMARY、Markdown evidence report 和 Citation RIS 的预期结构，不要实际检索或写文件。""",
    ),
    SmokePrompt(
        "pubmed-readiness",
        "PubMed MCP readiness/status check",
        f"""/pubmed-literature-search 做一次 PubMed MCP readiness check。\n{COMMON_GUARDRAIL}\n请只报告当前会话是否能看到 PubMed MCP tools，例如 search、details、extract、related、fulltext detection/download；不要执行下载；如果没有 status 工具，就用最小只读能力检查说明。""",
    ),
    SmokePrompt(
        "pubmed-search",
        "PubMed chat-only search",
        f"""/pubmed-literature-search 只在聊天输出，不要生成文件：检索近 5 年 PCOS sedentary behavior 的 PubMed 文献，最多返回 5 条候选。\n{COMMON_GUARDRAIL}\n先单独执行 PubMed search；检查 PMID 列表后，再单独对候选 PMID 调用 details/extract。只有实际完成 PMID metadata inspection 的文献才能标记为 inspected。""",
    ),
    SmokePrompt(
        "pubmed-export-crosscheck-dry-run",
        "PubMed default export with Zotero cross-check route dry run",
        f"""/pubmed-literature-search 只读路由验证，不要生成文件：如果用户请求“检索 PubMed 近 5 年 PCOS sedentary behavior 文献”，请说明当前默认应执行 PubMed search、PMID metadata inspection、Zotero optional cross-check，并生成 PubMed Markdown report + RIS。\n{COMMON_GUARDRAIL}\n请只输出预期路由、PMID Inspection Ledger、Zotero Local Library Cross-Check 表、PubMed-only RIS 纳入规则、以及预期相对路径格式 `pubmed-literature-output/{{brief_topic_slug}}_{{YYYY-MM-DD_HHMMSS}}/{{brief_topic_slug}}_{{YYYY-MM-DD_HHMMSS}}_pubmed_review.md` 和 `_references.ris`；不要实际写入 Markdown/RIS。""",
    ),
    SmokePrompt(
        "zotero-pubmed-fallback",
        "Zotero workflow with PubMed unavailable fallback",
        f"""/zotero-evidence-review 只在聊天输出，不要生成文件：先检索 Zotero 本地库，为下面这句话找证据；如果 PubMed MCP 不可用，请只给出可复制 PubMed query，不要声称已完成 PubMed 检索。\n{COMMON_GUARDRAIL}\n句子：Sedentary behaviour may be associated with cardiometabolic and reproductive health risks in PCOS, but causal evidence should be described cautiously.\n请输出 claim 拆解、Zotero 候选证据、PubMed 状态、以及哪些 claim 仍需要人工/全文复核。""",
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Print safe manual MCP smoke-test prompts")
    parser.add_argument("--list", action="store_true", help="List prompt keys without printing full prompts")
    parser.add_argument("--prompt", choices=[prompt.key for prompt in PROMPTS], help="Print one prompt by key")
    parser.add_argument("--check", action="store_true", help="Validate prompt guardrail phrases and exit")
    return parser.parse_args()


def validate_prompts() -> list[str]:
    required = [
        "只读",
        "不要修改 Zotero",
        "不要生成文件",
        "unavailable",
        "不要伪造 PMID",
        "Tool skipped because a previous tool call",
        "分步进行",
        "不要同批调度依赖调用",
    ]
    problems: list[str] = []
    for prompt in PROMPTS:
        for phrase in required:
            if phrase not in prompt.text:
                problems.append(f"{prompt.key}: missing guardrail phrase {phrase!r}")
    return problems


def print_prompt(prompt: SmokePrompt) -> None:
    print(f"## {prompt.title} ({prompt.key})")
    print("```text")
    print(prompt.text)
    print("```")


def main() -> None:
    args = parse_args()
    if args.check:
        problems = validate_prompts()
        if problems:
            for problem in problems:
                print(f"❌ {problem}")
            raise SystemExit(1)
        print("✅ smoke prompts contain required safety and sequencing guardrails")
        return

    if args.list:
        for prompt in PROMPTS:
            print(f"{prompt.key}\t{prompt.title}")
        return

    prompts = [prompt for prompt in PROMPTS if prompt.key == args.prompt] if args.prompt else PROMPTS
    for index, prompt in enumerate(prompts):
        if index:
            print()
        print_prompt(prompt)


if __name__ == "__main__":
    main()
