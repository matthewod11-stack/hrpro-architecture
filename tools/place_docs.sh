#!/bin/zsh
set -euo pipefail

# === VERIFY CANONICAL DOCS ===
for f in docs/PRD/PRD_v4.0_unified_numbered.md docs/Architecture/Architecture_v4.1_unified.md docs/UI_Framework/UIFramework_v4.0_unified_numbered.md; do
  if [[ ! -f "$f" ]]; then
    echo "Missing canonical file: $f"
    exit 1
  fi
done
if [[ ! -d docs/adr ]]; then
  echo "Missing canonical ADR folder: docs/adr"
  exit 1
fi
echo "All canonical docs present."

# === PREPARE EXTERNAL KB FOLDER ===
mkdir -p knowledge_base/sources

# === SYNC (DRY RUN) ===
rsync -avun --include='*/' --include='*.md' --include='*.MD' --exclude='*' ~/Desktop/knowledge_base/ knowledge_base/sources/

echo "Proceed with actual copy? [y/N]"
read ans
if [[ "$ans" != "y" && "$ans" != "Y" ]]; then
  echo "Aborted. No files copied."
  exit 0
fi

# === SYNC (REAL COPY) ===
rsync -avu --include='*/' --include='*.md' --include='*.MD' --exclude='*' ~/Desktop/knowledge_base/ knowledge_base/sources/

# === POST-SYNC CHECKS ===
file_count=$(find knowledge_base/sources/ -type f \( -iname '*.md' -o -iname '*.MD' \) | wc -l)
total_size=$(find knowledge_base/sources/ -type f \( -iname '*.md' -o -iname '*.MD' \) -exec du -ch {} + | grep total$ | awk '{print $1}')
echo "Markdown files copied: $file_count"
echo "Total size: $total_size"

echo "Sample file paths:"
find knowledge_base/sources/ -type f \( -iname '*.md' -o -iname '*.MD' \) | head -10 | sed 's|knowledge_base/sources/||'

# === .GITIGNORE CHECK ===
if grep -q 'knowledge_base/sources/**/*.pdf' .gitignore && grep -q 'knowledge_base/sources/**/*.PDF' .gitignore; then
  echo ".gitignore correctly excludes PDFs."
else
  echo "WARNING: .gitignore does not exclude PDFs. Please update."
fi

# === REBUILD KB & INDEX ===
make kb-build
make kb-index
make kb-retrieve

# === BUILD REPORT SNIPPET ===
head -10 knowledge_base/build_report.md
