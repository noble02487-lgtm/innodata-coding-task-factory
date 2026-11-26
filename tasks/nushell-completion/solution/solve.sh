#!/bin/bash
# Apply the reference implementation patch to the repository at /app.
set -e
cd /app
PATCH=""
for candidate in "$(dirname "$0")/solution.patch" /solution/solution.patch ./solution.patch; do
    if [ -f "$candidate" ]; then PATCH="$candidate"; break; fi
done
if [ -z "$PATCH" ]; then echo "solution.patch not found" >&2; exit 1; fi
git apply "$PATCH"
echo "Reference solution applied from $PATCH"
