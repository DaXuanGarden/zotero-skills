#!/usr/bin/env python3
"""Run local read-only quality gates for Zotero/PubMed skills."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable or "python3"


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def run_step(label: str, command: list[str]) -> int:
    print(f"\n==> {label}", flush=True)
    print("$ " + " ".join(command), flush=True)
    completed = subprocess.run(command, cwd=REPO_ROOT, check=False)
    if completed.returncode == 0:
        print(f"✅ {label} passed")
    else:
        print(f"❌ {label} failed with exit code {completed.returncode}")
    return completed.returncode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run local read-only quality gates for Zotero/PubMed skills")
    parser.add_argument(
        "--output-warnings",
        choices=("fail", "warn", "skip"),
        default="fail",
        help="How to handle output audit/RIS warnings: fail strictly, warn without failing, or skip output checks",
    )
    parser.add_argument(
        "--ignore-output-warnings-before",
        metavar="YYYY-MM-DD",
        help="Ignore output audit/RIS warnings for packages dated before this cutoff; errors still fail",
    )
    return parser.parse_args()


def existing_dirs(*names: str) -> list[str]:
    return [name for name in names if (REPO_ROOT / name).is_dir()]


def append_output_warning_args(command: list[str], args: argparse.Namespace) -> list[str]:
    command = command.copy()
    if args.ignore_output_warnings_before:
        command.extend(["--ignore-before", args.ignore_output_warnings_before])
    if args.output_warnings == "fail":
        command.append("--fail-on-warnings")
    return command


def main() -> None:
    args = parse_args()
    steps: list[tuple[str, list[str]]] = [
        ("Validate zotero-evidence-review skill", [PYTHON, "scripts/validate-skill.py"]),
        ("Validate pubmed-literature-search skill", [PYTHON, "scripts/validate-pubmed-skill.py"]),
    ]

    if args.output_warnings == "skip":
        print("Output package checks skipped (--output-warnings skip).", flush=True)
    else:
        if (REPO_ROOT / "zotero-evidence-output").is_dir():
            steps.append(
                (
                    "Audit Zotero evidence output packages",
                    append_output_warning_args(
                        [PYTHON, "scripts/evidence_output_audit.py", "--input", "zotero-evidence-output"],
                        args,
                    ),
                )
            )

        if (REPO_ROOT / "pubmed-literature-output").is_dir():
            steps.append(
                (
                    "Audit PubMed literature output packages",
                    append_output_warning_args(
                        [PYTHON, "scripts/pubmed_output_audit.py", "--input", "pubmed-literature-output"],
                        args,
                    ),
                )
            )

        ris_dirs = existing_dirs("zotero-evidence-output", "pubmed-literature-output")
        if ris_dirs:
            steps.append(
                (
                    "Lint generated RIS files",
                    append_output_warning_args([PYTHON, "scripts/ris_lint.py", *ris_dirs], args),
                )
            )

    failures = 0
    for label, command in steps:
        failures += 1 if run_step(label, command) != 0 else 0

    if failures:
        print(f"\nQuality gate failed: {failures} step(s) returned non-zero.")
        raise SystemExit(1)

    print("\nAll local quality gates passed.")


if __name__ == "__main__":
    main()
