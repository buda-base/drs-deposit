#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/deploy_project.sh TARGET_DIR [options]

Copy a minimal deployment set into TARGET_DIR for Docker Compose runs.

Options:
  --source DIR              Source project directory (default: repo root)
  --delete                  Delete files in target that no longer exist in source
  --dry-run                 Show what would be copied without changing files
  --no-ssh-precheck         Skip initial remote mkdir precheck (remote targets)
  --help                    Show this help

Notes:
- Synced paths are fixed to:
  - .env
  - Dockerfile
  - Dockerfile.dev
  - docker-compose.yaml
  - docker-compose-dev.yaml
  - docker-compose-secrets.yaml
  - dags/
  - plugins/
  - scripts/
  - utils/
- --delete removes stale files only inside synced directories.
EOF
}

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
DEFAULT_SOURCE=$(cd "$SCRIPT_DIR/.." && pwd)

TARGET_DIR=""

SOURCE_DIR="$DEFAULT_SOURCE"
DELETE_MODE=0
DRY_RUN=0
NO_SSH_PRECHECK=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h)
      usage
      exit 0
      ;;
    --source)
      SOURCE_DIR=${2:-}
      shift 2
      ;;
    --delete)
      DELETE_MODE=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --no-ssh-precheck)
      NO_SSH_PRECHECK=1
      shift
      ;;
    --*)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
    *)
      if [[ -z "$TARGET_DIR" ]]; then
        TARGET_DIR=$1
      else
        echo "Unexpected extra argument: $1" >&2
        usage
        exit 1
      fi
      shift
      ;;
  esac
done

if [[ -z "$TARGET_DIR" ]]; then
  echo "TARGET_DIR is required" >&2
  usage
  exit 1
fi

if [[ -z "$SOURCE_DIR" || ! -d "$SOURCE_DIR" ]]; then
  echo "Source directory not found: $SOURCE_DIR" >&2
  exit 1
fi

if ! command -v rsync >/dev/null 2>&1; then
  echo "rsync is required but not found in PATH" >&2
  exit 1
fi

TARGET_IS_REMOTE=0
REMOTE_HOST=""
REMOTE_BASE_PATH=""
if [[ "$TARGET_DIR" == *:* ]]; then
  TARGET_IS_REMOTE=1
  REMOTE_HOST=${TARGET_DIR%%:*}
  REMOTE_BASE_PATH=${TARGET_DIR#*:}
fi

require_ssh_for_remote_ops() {
  if [[ $TARGET_IS_REMOTE -eq 1 ]] && ! command -v ssh >/dev/null 2>&1; then
    echo "ssh is required for this remote operation but not found in PATH" >&2
    exit 1
  fi
}

quote_for_single_quotes() {
  printf "%s" "$1" | sed "s/'/'\\''/g"
}

ensure_target_root_exists() {
  if [[ $TARGET_IS_REMOTE -eq 1 ]]; then
    if [[ $NO_SSH_PRECHECK -eq 1 ]]; then
      return
    fi
    require_ssh_for_remote_ops
    local escaped
    escaped=$(quote_for_single_quotes "$REMOTE_BASE_PATH")
    ssh "$REMOTE_HOST" "mkdir -p '$escaped'"
  else
    mkdir -p "$TARGET_DIR"
  fi
}

delete_target_file() {
  local rel_path=$1
  if [[ $TARGET_IS_REMOTE -eq 1 ]]; then
    require_ssh_for_remote_ops
    local escaped
    escaped=$(quote_for_single_quotes "$REMOTE_BASE_PATH/$rel_path")
    ssh "$REMOTE_HOST" "rm -f '$escaped'"
  else
    rm -f "$TARGET_DIR/$rel_path"
  fi
}

delete_target_dir() {
  local rel_path=$1
  if [[ $TARGET_IS_REMOTE -eq 1 ]]; then
    require_ssh_for_remote_ops
    local escaped
    escaped=$(quote_for_single_quotes "$REMOTE_BASE_PATH/$rel_path")
    ssh "$REMOTE_HOST" "rm -rf '$escaped'"
  else
    rm -rf "$TARGET_DIR/$rel_path"
  fi
}

apply_owner_if_exists() {
  local rel_path=$1
  local owner_spec=$2
  local owner_uid=${owner_spec%%:*}
  if [[ $TARGET_IS_REMOTE -eq 1 ]]; then
    require_ssh_for_remote_ops
    local escaped
    escaped=$(quote_for_single_quotes "$REMOTE_BASE_PATH/$rel_path")
    ssh "$REMOTE_HOST" "
      if [ -e '$escaped' ]; then
        if chown -R '$owner_spec' '$escaped' 2>/dev/null; then
          exit 0
        fi

        echo 'chown not permitted on $rel_path; attempting ACL/permission fallback' >&2
        if command -v setfacl >/dev/null 2>&1; then
          setfacl -R -m u:$owner_uid:rX '$escaped' && setfacl -R -m d:u:$owner_uid:rX '$escaped' 2>/dev/null || true
          exit 0
        fi

        # Final fallback when ACL tools are unavailable.
        find '$escaped' -type d -exec chmod 755 {} +
        find '$escaped' -type f -exec chmod 644 {} +
      fi
    "
  else
    if [[ -e "$TARGET_DIR/$rel_path" ]]; then
      if chown -R "$owner_spec" "$TARGET_DIR/$rel_path" 2>/dev/null; then
        return
      fi

      echo "chown not permitted on $TARGET_DIR/$rel_path; attempting ACL/permission fallback" >&2
      if command -v setfacl >/dev/null 2>&1; then
        setfacl -R -m u:"$owner_uid":rX "$TARGET_DIR/$rel_path" || true
        setfacl -R -m d:u:"$owner_uid":rX "$TARGET_DIR/$rel_path" 2>/dev/null || true
      else
        find "$TARGET_DIR/$rel_path" -type d -exec chmod 755 {} +
        find "$TARGET_DIR/$rel_path" -type f -exec chmod 644 {} +
      fi
    fi
  fi
}

ensure_target_root_exists

RSYNC_ARGS=(
  -a
  --human-readable
  --itemize-changes
  --mkpath
  --exclude=__pycache__/
)

if [[ $DRY_RUN -eq 1 ]]; then
  RSYNC_ARGS+=(--dry-run)
fi

echo "Syncing project"
echo "  from: $SOURCE_DIR/"
echo "  to:   $TARGET_DIR/"

SYNC_FILES=(
  ".env"
  "Dockerfile"
  "Dockerfile.dev"
  "docker-compose.yaml"
  "docker-compose-dev.yaml"
  "docker-compose-secrets.yaml"
)

SYNC_DIRS=(
  "dags"
  "plugins"
  "scripts"
  "utils"
  "secrets"
  "config"
)

CHOWN_AIRFLOW=(
  "secrets"
)

AIRFLOW_OWNER_DEFAULT="${AIRFLOW_UID:-50000}:0"

for rel_file in "${SYNC_FILES[@]}"; do
  src_file="$SOURCE_DIR/$rel_file"
  dst_file="$TARGET_DIR/$rel_file"

  if [[ -f "$src_file" ]]; then
    rsync "${RSYNC_ARGS[@]}" "$src_file" "$dst_file"
  elif [[ $DELETE_MODE -eq 1 ]]; then
    delete_target_file "$rel_file"
  fi
done

for rel_dir in "${SYNC_DIRS[@]}"; do
  src_dir="$SOURCE_DIR/$rel_dir"
  dst_dir="$TARGET_DIR/$rel_dir"

  if [[ -d "$src_dir" ]]; then
    DIR_ARGS=("${RSYNC_ARGS[@]}")
    if [[ $DELETE_MODE -eq 1 ]]; then
      DIR_ARGS+=(--delete)
    fi
    rsync "${DIR_ARGS[@]}" "$src_dir/" "$dst_dir/"
  elif [[ $DELETE_MODE -eq 1 ]]; then
    delete_target_dir "$rel_dir"
  fi
done

# Always normalize ownership for selected deploy paths.
for rel in "${CHOWN_AIRFLOW[@]}"; do
  apply_owner_if_exists "$rel" "$AIRFLOW_OWNER_DEFAULT"
done

echo "Deploy sync complete."
