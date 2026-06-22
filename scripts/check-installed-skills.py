#!/usr/bin/env python3
"""Detect drift between repository skills and installed ZCode/OpenCode copies."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()
SKILLS = ("zotero-evidence-review", "pubmed-literature-search")


@dataclass(frozen=True)
class Target:
    name: str
    root: Path
    install_hint: str


TARGETS = {
    "zcode": Target("zcode", HOME / ".zcode/skills", "scripts/install-skill.sh --skill all-skills --target zcode --backup"),
    "opencode": Target(
        "opencode",
        HOME / ".config/opencode/skills",
        "scripts/install-skill.sh --skill all-skills --target opencode --backup",
    ),
    "project": Target(
        "project",
        REPO_ROOT / ".opencode/skills",
        "scripts/install-skill.sh --skill all-skills --target project --backup",
    ),
}


@dataclass
class SkillMeta:
    path: Path
    exists: bool
    sha256: str | None = None
    name: str | None = None
    version: str | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check installed ZCode/OpenCode skill copies for drift")
    parser.add_argument(
        "--target",
        choices=("zcode", "opencode", "project", "all"),
        default="all",
        help="Installed skill target to inspect",
    )
    parser.add_argument(
        "--mode",
        choices=("warn", "fail"),
        default="warn",
        help="Whether drift/missing installed skills should return success or failure",
    )
    return parser.parse_args()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def frontmatter_value(text: str, key: str) -> str | None:
    if not text.startswith("---"):
        return None
    match = re.search(r"^---\s*\n(.*?)\n---\s*\n", text, flags=re.DOTALL)
    if not match:
        return None
    for line in match.group(1).splitlines():
        if line.strip().startswith(f"{key}:"):
            value = line.split(":", 1)[1].strip()
            return value.strip('"\'')
    return None


def read_meta(path: Path) -> SkillMeta:
    if not path.exists():
        return SkillMeta(path=path, exists=False)
    text = path.read_text(encoding="utf-8")
    return SkillMeta(
        path=path,
        exists=True,
        sha256=sha256_text(text),
        name=frontmatter_value(text, "name"),
        version=frontmatter_value(text, "version"),
    )


def short_hash(value: str | None) -> str:
    return value[:12] if value else "-"


def selected_targets(target: str) -> list[Target]:
    if target == "all":
        return [TARGETS[name] for name in ("zcode", "opencode", "project")]
    return [TARGETS[target]]


def main() -> None:
    args = parse_args()
    drift_count = 0
    missing_count = 0

    print("Installed skill drift check (read-only).")
    print(f"Repository root: {REPO_ROOT}")

    repo_meta = {skill: read_meta(REPO_ROOT / skill / "SKILL.md") for skill in SKILLS}
    for skill, meta in repo_meta.items():
        if not meta.exists:
            print(f"❌ repo skill missing: {skill} at {meta.path}")
            raise SystemExit(2)
        print(f"\nRepo {skill}: version={meta.version or '-'} sha256={short_hash(meta.sha256)} path={meta.path}")

        for target in selected_targets(args.target):
            installed_path = target.root / skill / "SKILL.md"
            installed = read_meta(installed_path)
            label = f"{target.name}:{skill}"
            if not installed.exists:
                missing_count += 1
                print(f"  ⚠️ {label}: missing at {installed_path}")
                continue

            same = installed.sha256 == meta.sha256
            if same:
                print(
                    f"  ✅ {label}: same version={installed.version or '-'} sha256={short_hash(installed.sha256)}"
                )
            else:
                drift_count += 1
                print(
                    f"  ⚠️ {label}: different repo={short_hash(meta.sha256)} installed={short_hash(installed.sha256)} "
                    f"installed_version={installed.version or '-'} path={installed_path}"
                )

    if drift_count or missing_count:
        print("\nRecommended sync commands:")
        for target in selected_targets(args.target):
            print(f"  {target.install_hint}")
        print("After syncing, fully restart ZCode/OpenCode or open a new session so skills and MCP tool lists reload.")
    else:
        print("\nAll checked installed skill copies match the repository versions.")

    if args.mode == "fail" and (drift_count or missing_count):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
