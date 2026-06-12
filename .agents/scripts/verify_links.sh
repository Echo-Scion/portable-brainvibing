#!/bin/bash
# Verify all view_file links in the .agents directories

echo "Verifying view_file links..."

PATHS=$(grep -hro "view_file [^ ]*" .agents/ --exclude="verify_links.sh" | sed -E "s/^view_file (.*)/\1/" | tr -d '\`' | sed "s/['\.\"]*$//" | sort | uniq)

ERROR=0

for FILE in $PATHS; do
    if [ ! -f "$FILE" ]; then
        echo "[ERROR] Missing file referenced by view_file: $FILE"
        ERROR=1
    fi
done

if [ $ERROR -eq 0 ]; then
    echo "[PASS] All view_file links are valid."
    exit 0
else
    echo "[FAIL] Broken links found."
    exit 1
fi
