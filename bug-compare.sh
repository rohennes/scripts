#!/usr/bin/env bash

# === CONFIGURATION ===
RELEASE_NOTES_FILE="/home/rohennes/openshift-docs/release_notes/ocp-4-19-release-notes.adoc"
JIRA_API_URL='https://issues.redhat.com/rest/api/2/search'

# === INPUT VALIDATION ===
if [[ -z "$1" ]]; then
  echo "Usage: $0 <JIRA component>"
  echo "Example: $0 'Bare Metal Hardware Provisioning'"
  exit 1
fi

COMPONENT="$1"

# Optional authentication (export env vars if needed)
# export JIRA_USER="you@example.com"
# export JIRA_TOKEN="your-api-token"

# === FUNCTIONS ===

extract_bugs_from_release_notes() {
  grep -oE 'OCPBUGS-[0-9]+' "$RELEASE_NOTES_FILE" | sort -u
}

fetch_bugs_from_jira() {
  local component="$1"
  local jql="project = \"OpenShift Bugs\" AND type = bug AND issueFunction in commented(\"by e-tool\") AND status in (ON_QA, Verified) AND (\"Release Note Type\" not in (\"CVE - Common Vulnerabilities and Exposures\", \"Developer Preview\", \"Release Note Not Required\") OR \"Release Note Type\" is EMPTY) AND component = \"$component\""

  # Encode the JQL string
  local encoded_jql
  encoded_jql=$(python3 -c "import urllib.parse; print(urllib.parse.quote('''$jql'''))")

  local auth=""
  if [[ -n "$JIRA_USER" && -n "$JIRA_TOKEN" ]]; then
    auth="-u $JIRA_USER:$JIRA_TOKEN"
  fi

  echo "=== Fetching JIRA bugs for component: $component ===" >&2
  curl -s $auth "$JIRA_API_URL?jql=$encoded_jql&fields=key&maxResults=1000" |
    jq -r '.issues[].key' |
    grep '^OCPBUGS-' |
    sort -u
}

compare_bugs() {
  local_file_bugs="$1"
  jira_bugs="$2"

  echo
  echo "=== Bugs in release notes but not in JIRA query (possibly incorrect) ==="
  comm -23 "$local_file_bugs" "$jira_bugs"

  echo
  echo "=== Bugs in JIRA query but missing from release notes (possibly missing) ==="
  comm -13 "$local_file_bugs" "$jira_bugs"
}

# === MAIN ===

TMP_LOCAL=$(mktemp)
TMP_JIRA=$(mktemp)

extract_bugs_from_release_notes > "$TMP_LOCAL"
fetch_bugs_from_jira "$COMPONENT" > "$TMP_JIRA"

compare_bugs "$TMP_LOCAL" "$TMP_JIRA"

rm -f "$TMP_LOCAL" "$TMP_JIRA"
