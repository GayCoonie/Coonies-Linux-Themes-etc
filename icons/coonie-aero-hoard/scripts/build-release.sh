#!/usr/bin/env bash
# Package the checked-out artwork. No network, donor checkout, or release input.
set -euo pipefail
project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
repo_root="$(cd -- "$project_root/../.." && pwd)"
output="${1:-$project_root/dist}"
mkdir -p "$output"
output="$(cd -- "$output" && pwd)"
python3 "$repo_root/scripts/validate_repository.py"
stage="$(mktemp -d)"
trap 'rm -rf -- "$stage"' EXIT
mkdir -p "$stage/portable" "$stage/deb/DEBIAN" "$stage/deb/usr/share/icons"
cp -a "$project_root/Coonie-Aero-Hoard" "$stage/portable/"
for name in install.sh uninstall.sh README.md CHANGELOG.md SOURCE-AND-LICENSES.md LICENSE; do
  cp -a "$project_root/$name" "$stage/portable/"
done
rm -f "$stage/portable/Coonie-Aero-Hoard/icon-theme.cache"
python3 "$project_root/scripts/audit_theme.py" "$stage/portable/Coonie-Aero-Hoard" --report "$stage/audit.md"
cp -a "$stage/portable/Coonie-Aero-Hoard" "$stage/deb/usr/share/icons/"
cp -a "$project_root/packaging/"{control,postinst,postrm} "$stage/deb/DEBIAN/"
chmod 0755 "$stage/deb/DEBIAN/"{postinst,postrm}
tar -czf "$output/Coonie-Aero-Hoard-1.1.2-from-source.tar.gz" -C "$stage/portable" .
dpkg-deb --root-owner-group -Zgzip --build "$stage/deb" "$output/coonie-aero-hoard-icon-theme_1.1.2_all.deb"
cp "$stage/audit.md" "$output/AUDIT.md"
(cd "$output" && sha256sum Coonie-Aero-Hoard-1.1.2-from-source.tar.gz coonie-aero-hoard-icon-theme_1.1.2_all.deb > SHA256SUMS)
printf 'Packaged checked-out artwork in %s\n' "$output"
