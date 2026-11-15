#!/usr/bin/env bash
# Prints what it reads and also adds it to the summary of the job (the page of the run) as a block of code, with a title. It does nothing
# more than print when there is no summary, as outside of GitHub Actions, and it never fails because of the summary.
#
#   bin/show_versions_linux.sh | bin/job_summary.sh "apt libraries"
set -uo pipefail

title=${1:-}
text=$(cat)
printf '%s\n' "$text"

summary=${GITHUB_STEP_SUMMARY:-}
if [ -n "$summary" ]; then
  # in MSYS2 the file of the summary has a path of Windows
  if command -v cygpath > /dev/null 2>&1; then
    summary=$(cygpath -u "$summary")
  fi
  {
    if [ -n "$title" ]; then
      printf '### %s\n\n' "$title"
    fi
    printf '```\n%s\n```\n\n' "$text"
  } >> "$summary" || true
fi
exit 0
