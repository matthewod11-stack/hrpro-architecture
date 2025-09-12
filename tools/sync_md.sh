#!/bin/zsh
set -e
SRC="$1"
DEST="$2"
if [[ -z "$SRC" || -z "$DEST" ]]; then
  echo "Usage: $0 <source_dir> <dest_dir>"
  exit 1
fi

mkdir -p "$DEST"
echo "Dry run: files to be copied from $SRC to $DEST (Markdown only):"
rsync -avun --include='*/' --include='*.md' --include='*.MD' --exclude='*' "$SRC/" "$DEST/"

echo "Proceed with actual copy? [y/N]"
read ans
if [[ "$ans" == "y" || "$ans" == "Y" ]]; then
  rsync -avu --include='*/' --include='*.md' --include='*.MD' --exclude='*' "$SRC/" "$DEST/"
  echo "Markdown files copied."
else
  echo "Aborted. No files copied."
fi
