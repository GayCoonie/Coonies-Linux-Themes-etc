#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
PARENT="$(dirname "$ROOT_DIR")"
NAME="darkcold-coonie-theme-2.2.2"
TEMP_DIR="$(mktemp -d)"
trap 'rm -rf -- "$TEMP_DIR"' EXIT
cd "$PARENT"
tar --exclude='.git' --exclude='*.tar.gz' --exclude='*.zip' -czf "$TEMP_DIR/$NAME.tar.gz" "$(basename "$ROOT_DIR")"
zip -qr "$TEMP_DIR/$NAME.zip" "$(basename "$ROOT_DIR")" -x '*/.git/*' '*.tar.gz' '*.zip'
mv "$TEMP_DIR/$NAME.tar.gz" "$ROOT_DIR/$NAME.tar.gz"
mv "$TEMP_DIR/$NAME.zip" "$ROOT_DIR/$NAME.zip"
printf '%s\n' "$ROOT_DIR/$NAME.tar.gz" "$ROOT_DIR/$NAME.zip"
