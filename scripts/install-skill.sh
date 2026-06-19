#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: scripts/install-skill.sh [--skill zotero-evidence-review|pubmed-literature-search|all-skills] [--target zcode|opencode|project|all] [--backup]

Install skills from this repository into a local skill directory.

Skills:
  zotero-evidence-review     Zotero-grounded evidence review workflow (default)
  pubmed-literature-search   PubMed MCP literature search workflow
  all-skills                 Install all repository skills

Targets:
  zcode     ~/.zcode/skills/<skill-name>
  opencode  ~/.config/opencode/skills/<skill-name>
  project   ./.opencode/skills/<skill-name>
  all       zcode + opencode + project

Options:
  --backup  If the target exists, copy it to <target>.backup-YYYYmmdd-HHMMSS before replacing it.
  -h, --help  Show this help.
USAGE
}

TARGET="zcode"
SKILL="zotero-evidence-review"
BACKUP=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skill)
      [[ $# -ge 2 ]] || { echo "Missing value for --skill" >&2; exit 2; }
      SKILL="$2"
      shift 2
      ;;
    --target)
      [[ $# -ge 2 ]] || { echo "Missing value for --target" >&2; exit 2; }
      TARGET="$2"
      shift 2
      ;;
    --backup)
      BACKUP=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

case "$TARGET" in
  zcode|opencode|project|all) ;;
  *)
    echo "Invalid target: $TARGET" >&2
    usage >&2
    exit 2
    ;;
esac

case "$SKILL" in
  zotero-evidence-review|pubmed-literature-search|all-skills) ;;
  *)
    echo "Invalid skill: $SKILL" >&2
    usage >&2
    exit 2
    ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

skill_names() {
  case "$SKILL" in
    all-skills)
      printf '%s\n' zotero-evidence-review pubmed-literature-search
      ;;
    *)
      printf '%s\n' "$SKILL"
      ;;
  esac
}

target_paths() {
  local skill_name="$1"
  case "$TARGET" in
    zcode)
      printf '%s\n' "$HOME/.zcode/skills/$skill_name"
      ;;
    opencode)
      printf '%s\n' "$HOME/.config/opencode/skills/$skill_name"
      ;;
    project)
      printf '%s\n' "$REPO_ROOT/.opencode/skills/$skill_name"
      ;;
    all)
      printf '%s\n' \
        "$HOME/.zcode/skills/$skill_name" \
        "$HOME/.config/opencode/skills/$skill_name" \
        "$REPO_ROOT/.opencode/skills/$skill_name"
      ;;
  esac
}

install_one() {
  local source_dir="$1"
  local dest="$2"
  local parent
  parent="$(dirname "$dest")"
  mkdir -p "$parent"

  if [[ -e "$dest" ]]; then
    if [[ "$BACKUP" == true ]]; then
      local stamp backup_path
      stamp="$(date +%Y%m%d-%H%M%S)"
      backup_path="${dest}.backup-${stamp}"
      cp -a "$dest" "$backup_path"
      echo "Backup created: $backup_path"
    fi
    rm -rf "$dest"
  fi

  cp -a "$source_dir" "$dest"
  echo "Installed: $dest"
}

while IFS= read -r skill_name; do
  source_dir="$REPO_ROOT/$skill_name"
  skill_file="$source_dir/SKILL.md"

  if [[ ! -f "$skill_file" ]]; then
    echo "Source skill not found: $skill_file" >&2
    exit 1
  fi

  while IFS= read -r dest; do
    install_one "$source_dir" "$dest"
  done < <(target_paths "$skill_name")
done < <(skill_names)
