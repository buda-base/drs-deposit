#!/bin/sh
set -eu

# Resolve any environment variable ending in _CMD by executing its command,
# then export the base variable name with the command output.
while IFS='=' read -r env_key env_value; do
  case "$env_key" in
    *_CMD)
      base_key=${env_key%_CMD}
      if [ -n "$env_value" ]; then
        resolved_value=$(sh -c "$env_value")
        export "$base_key=$resolved_value"
      fi
      ;;
  esac
done <<EOF
$(env)
EOF

exec /entrypoint "$@"