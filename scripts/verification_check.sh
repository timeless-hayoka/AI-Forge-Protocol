#!/bin/bash

# A.F.P Documentation Validation Script
# This script scans for placeholders that need manual data injection.

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}--- AI FORGE PROTOCOL: Documentation Validation ---${NC}"

FILES_TO_CHECK=(
    "README.md.new"
    "COMMUNITY_OUTREACH.md"
)

PLACEHOLDER_PATTERN="\[INSERT [A-Z ]+\]"

FOUND_EMPTY=0

for file in "${FILES_TO_CHECK[@]}"; do
    if [ -f "$file" ]; then
        echo -e "\nChecking ${GREEN}$file${NC}..."
        
        # Search for placeholders and show line numbers
        matches=$(grep -nE "$PLACEHOLDER_PATTERN" "$file")
        
        if [ -n "$matches" ]; then
            echo -e "${RED}Found empty placeholders:${NC}"
            echo "$matches"
            FOUND_EMPTY=1
        else
            echo -e "${GREEN}No placeholders found in this file.${NC}"
        fi
    else
        echo -e "${RED}Error: File $file not found.${NC}"
    fi
done

echo -e "\n---"
if [ $FOUND_EMPTY -eq 1 ]; then
    echo -e "${YELLOW}ACTION REQUIRED: Fill the placeholders listed above before pushing to production.${NC}"
else
    echo -e "${GREEN}VALIDATION PASSED: All documentation is grounded and filled.${NC}"
fi
echo -e "---"
