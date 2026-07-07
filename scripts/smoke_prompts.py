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
