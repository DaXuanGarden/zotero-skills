#!/usr/bin/env python3
"""Remove timestamped backup copies created by install-skill.sh.

The command is intentionally dry-run by default.  It only considers the
repository's known skills and only removes directories directly below the
selected skill root whose names match ``<skill>.backup-*``.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()
SKILLS = (
    "zotero-evidence-review",
    "zotero-literature-learning",
    "zotero-manuscript-thinking",
    "pubmed-literature-search",
)

TARGET_ROOTS = {
    "codex": HOME / ".codex/skills",
    "zcode": HOME / ".zcode/skills",
    "opencode": HOME / ".config/opencode/skills",
    "project": REPO_ROOT / ".opencode/skills",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Find and remove timestamped backups for the repository's installed skills"
    )
    parser.add_argument(
        "--target",
        choices=(*TARGET_ROOTS, "all"),
        default="codex",
        help="Skill root to inspect (default: codex)",
    )
    parser.add_argument(
        "--skill",
        choices=(*SKILLS, "all-skills"),
        default="all-skills",
        help="Repository skill whose backups should be inspected",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually remove the listed backup directories; omit for a dry run",
    )
    return parser.parse_args()


def selected_roots(target: str) -> list[tuple[str, Path]]:
    if target == "all":
        return list(TARGET_ROOTS.items())
    return [(target, TARGET_ROOTS[target])]


def selected_skills(skill: str) -> tuple[str, ...]:
    return SKILLS if skill == "all-skills" else (skill,)


def backup_paths(root: Path, skill: str) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(
        path
        for path in root.glob(f"{skill}.backup-*")
        if path.parent == root and (path.is_dir() or path.is_symlink())
    )


def main() -> int:
    args = parse_args()
    found: list[tuple[str, Path]] = []

    for target, root in selected_roots(args.target):
        for skill in selected_skills(args.skill):
            for path in backup_paths(root, skill):
                found.append((target, path))

    if not found:
        print("No timestamped skill backups found.")
        return 0

    action = "Removing" if args.apply else "Would remove"
    print(f"{action} {len(found)} timestamped backup director{'y' if len(found) == 1 else 'ies'}:")
    for target, path in found:
        print(f"  {target}: {path}")

    if not args.apply:
        print("Dry run only. Re-run with --apply to remove these backups.")
        return 0

    for _, path in found:
        if path.is_symlink():
            path.unlink()
        else:
            shutil.rmtree(path)

    print(f"Removed {len(found)} timestamped skill backups.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
