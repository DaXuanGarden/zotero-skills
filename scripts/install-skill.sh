#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: scripts/install-skill.sh [--target zcode|opencode|project|all] [--backup]

Install zotero-evidence-review from this repository into a local skill directory.

Targets:
  zcode     ~/.zcode/skills/zotero-evidence-review
  opencode  ~/.config/opencode/skills/zotero-evidence-review
  project   ./.opencode/skills/zotero-evidence-review
  all       zcode + opencode + project

Options:
  --backup  If the target exists, copy it to <target>.backup-YYYYmmdd-HHMMSS before replacing it.
  -h, --help  Show this help.
USAGE
}

TARGET="zcode"
BACKUP=false

while [[ $# -gt 0 ]]; do
  case "$1" in
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

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCE_DIR="$REPO_ROOT/zotero-evidence-review"
SKILL_FILE="$SOURCE_DIR/SKILL.md"

if [[ ! -f "$SKILL_FILE" ]]; then
  echo "Source skill not found: $SKILL_FILE" >&2
  exit 1
fi

target_paths() {
  case "$TARGET" in
    zcode)
      printf '%s\n' "$HOME/.zcode/skills/zotero-evidence-review"
      ;;
    opencode)
      printf '%s\n' "$HOME/.config/opencode/skills/zotero-evidence-review"
      ;;
    project)
      printf '%s\n' "$REPO_ROOT/.opencode/skills/zotero-evidence-review"
      ;;
    all)
      printf '%s\n' \
        "$HOME/.zcode/skills/zotero-evidence-review" \
        "$HOME/.config/opencode/skills/zotero-evidence-review" \
        "$REPO_ROOT/.opencode/skills/zotero-evidence-review"
      ;;
  esac
}

install_one() {
  local dest="$1"
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

  cp -a "$SOURCE_DIR" "$dest"
  echo "Installed: $dest"
}

while IFS= read -r dest; do
  install_one "$dest"
done < <(target_paths)
