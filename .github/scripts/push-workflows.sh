#!/usr/bin/env bash
set -euo pipefail
: "${GH_TOKEN:?PAT_TOKEN is required to publish workflow changes}"
: "${GITHUB_REPOSITORY:?Repository is required}"
# Keep the credential out of command-line arguments and on-disk configuration.
ASKPASS=$(mktemp)
trap 'rm -f "$ASKPASS"' EXIT
cat > "$ASKPASS" <<'ASKPASS_SCRIPT'
#!/usr/bin/env bash
case "$1" in
  *Username*) printf '%s\n' 'x-access-token' ;;
  *Password*) printf '%s\n' "$GH_TOKEN" ;;
  *) exit 1 ;;
esac
ASKPASS_SCRIPT
chmod 700 "$ASKPASS"
export GIT_ASKPASS="$ASKPASS" GIT_TERMINAL_PROMPT=0
# Clear inherited helpers/headers for this command only. Do not change secrets.
if ! git -c credential.helper= -c http.https://github.com/.extraheader= \
  push "https://github.com/${GITHUB_REPOSITORY}.git" HEAD:refs/heads/main; then
  echo "::error::Workflow push failed. Verify PAT validity, Contents/Workflows write access, and branch protection. No credential values were logged."
  exit 1
fi
