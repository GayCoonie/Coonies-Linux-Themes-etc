#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
workspace_root="$(cd -- "$project_root/.." && pwd)"
sources_root="${COONIE_AERO_SOURCES:-$workspace_root/sources}"
dist_root="$project_root/dist"
theme_name="Coonie-Aero-Hoard"
version="1.1.2"
temp_root="$(mktemp -d -p "$project_root" .release-work.XXXXXX)"

cleanup() {
  rm -rf -- "$temp_root" 2>/dev/null || true
}
trap cleanup EXIT

mkdir -p "$dist_root"
rm -f -- \
  "$dist_root/${theme_name}-${version}.tar.xz" \
  "$dist_root/coonie-aero-hoard-icon-theme_${version}_all.deb" \
  "$dist_root/${theme_name}-${version}-source.tar.xz" \
  "$dist_root/${theme_name}-${version}-preview.png" \
  "$dist_root/${theme_name}-${version}-AUDIT.md" \
  "$dist_root/${theme_name}-${version}-summary.json" \
  "$dist_root/${theme_name}-${version}-SHA256SUMS.txt"
python3 "$project_root/scripts/build_theme.py" \
  --sources "$sources_root" \
  --output "$temp_root/built" \
  --project-root "$project_root"

theme_root="$temp_root/built/$theme_name"
python3 "$project_root/scripts/write_source_commits.py" \
  "$sources_root" "$theme_root/manifest/source-commits.json"

gtk-update-icon-cache -f -t "$theme_root" >/dev/null
python3 "$project_root/scripts/audit_theme.py" \
  "$theme_root" --report "$theme_root/AUDIT.md"

python3 "$project_root/scripts/make_preview.py" \
  "$theme_root" "$temp_root/preview.png"

xz -9e "$theme_root/manifest/icons.jsonl"

release_root="$temp_root/release"
mkdir -p "$release_root"
cp -a "$theme_root" "$release_root/$theme_name"
cp "$project_root/install.sh" "$release_root/install.sh"
cp "$project_root/uninstall.sh" "$release_root/uninstall.sh"
cp "$project_root/README.md" "$release_root/README.md"
cp "$project_root/CHANGELOG.md" "$release_root/CHANGELOG.md"
cp "$project_root/SOURCE-AND-LICENSES.md" "$release_root/SOURCE-AND-LICENSES.md"
cp "$temp_root/preview.png" "$release_root/preview.png"
chmod 0755 "$release_root/install.sh" "$release_root/uninstall.sh"

(cd "$release_root" && find . -type f -print0 | LC_ALL=C sort -z | \
  tar --null --no-recursion --mtime='UTC 2026-08-29' --owner=0 --group=0 --numeric-owner \
    -cJf "$dist_root/${theme_name}-${version}.tar.xz" -T -)

deb_root="$temp_root/deb"
mkdir -p "$deb_root/DEBIAN" "$deb_root/usr/share/icons"
cp -a "$theme_root" "$deb_root/usr/share/icons/$theme_name"
cp "$project_root/packaging/control" "$deb_root/DEBIAN/control"
cp "$project_root/packaging/postinst" "$deb_root/DEBIAN/postinst"
cp "$project_root/packaging/postrm" "$deb_root/DEBIAN/postrm"
chmod 0755 "$deb_root/DEBIAN/postinst" "$deb_root/DEBIAN/postrm"
dpkg-deb --root-owner-group --build "$deb_root" "$dist_root/coonie-aero-hoard-icon-theme_${version}_all.deb" >/dev/null

package_verify="$temp_root/package-verify"
mkdir -p "$package_verify/archive" "$package_verify/deb"
tar -xJf "$dist_root/${theme_name}-${version}.tar.xz" -C "$package_verify/archive"
dpkg-deb -x "$dist_root/coonie-aero-hoard-icon-theme_${version}_all.deb" "$package_verify/deb"
python3 "$project_root/scripts/audit_theme.py" \
  "$package_verify/archive/$theme_name" --report "$package_verify/archive-audit.md" >/dev/null
python3 "$project_root/scripts/audit_theme.py" \
  "$package_verify/deb/usr/share/icons/$theme_name" --report "$package_verify/deb-audit.md" >/dev/null

source_stage="$temp_root/source"
mkdir -p "$source_stage/Coonie-Aero-Hoard-src"
cp -a "$project_root/README.md" "$project_root/CHANGELOG.md" "$project_root/SOURCE-AND-LICENSES.md" "$project_root/LICENSE" \
  "$project_root/install.sh" "$project_root/uninstall.sh" "$project_root/scripts" "$project_root/packaging" \
  "$source_stage/Coonie-Aero-Hoard-src/"
(cd "$source_stage" && find . -type f -print0 | LC_ALL=C sort -z | \
  tar --null --no-recursion --mtime='UTC 2026-08-29' --owner=0 --group=0 --numeric-owner \
    -cJf "$dist_root/${theme_name}-${version}-source.tar.xz" -T -)

cp "$temp_root/preview.png" "$dist_root/${theme_name}-${version}-preview.png"
cp "$theme_root/AUDIT.md" "$dist_root/${theme_name}-${version}-AUDIT.md"
cp "$theme_root/manifest/summary.json" "$dist_root/${theme_name}-${version}-summary.json"

(cd "$dist_root" && sha256sum \
  "${theme_name}-${version}.tar.xz" \
  "coonie-aero-hoard-icon-theme_${version}_all.deb" \
  "${theme_name}-${version}-source.tar.xz" \
  "${theme_name}-${version}-preview.png" \
  "${theme_name}-${version}-AUDIT.md" \
  "${theme_name}-${version}-summary.json" \
  > "${theme_name}-${version}-SHA256SUMS.txt")

echo "Release written to $dist_root"
