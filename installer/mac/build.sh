#!/bin/bash
# Build "Studio Lab.app" and a drag-to-Applications .dmg on a Mac (used by .github/workflows/installers.yml).
#   installer/mac/build.sh <python-build-standalone install_only tarball> <label, e.g. AppleSilicon> <version>
# Run from the repository root. Output: dist/StudioLab-<version>-Mac-<label>.dmg
set -euo pipefail
PYTAR="$1"; LABEL="$2"; VER="$3"
APP="build/mac/Studio Lab.app"
rm -rf build/mac && mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources/app" dist

# the program (exactly what's committed) and a private Python with everything Studio Lab uses
git archive HEAD | tar -x -C "$APP/Contents/Resources/app"
tar -xzf "$PYTAR" -C "$APP/Contents/Resources"                      # -> Resources/python
PY="$APP/Contents/Resources/python/bin/python3"
export PYTHONPYCACHEPREFIX="$PWD/build/pycache"
"$PY" -m pip install --disable-pip-version-check --no-warn-script-location -q \
      -r "$APP/Contents/Resources/app/requirements.txt" pedalboard soundfile lameenc
# optional: numba (fast analog ladder filter + reverb). Only where a ready-made wheel exists (not on every Intel Mac).
"$PY" -m pip install --disable-pip-version-check --no-warn-script-location -q --only-binary=:all: numba \
      || echo "numba not available here - the app uses its fallback filter / reverb"
"$PY" -c "import numpy, scipy, pedalboard, soundfile, lameenc; print('bundled python ok')"

cp installer/mac/launcher.sh "$APP/Contents/MacOS/Studio Lab"
chmod +x "$APP/Contents/MacOS/Studio Lab"

# icon
ICS="build/mac/icon.iconset"; mkdir -p "$ICS"
for s in 16 32 128 256 512; do
  sips -z $s $s installer/icon.png --out "$ICS/icon_${s}x${s}.png" >/dev/null
  sips -z $((s * 2)) $((s * 2)) installer/icon.png --out "$ICS/icon_${s}x${s}@2x.png" >/dev/null
done
iconutil -c icns "$ICS" -o "$APP/Contents/Resources/studio-lab.icns"

cat > "$APP/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleName</key><string>Studio Lab</string>
  <key>CFBundleDisplayName</key><string>Studio Lab</string>
  <key>CFBundleIdentifier</key><string>io.github.kefirman9000.studiolab</string>
  <key>CFBundleVersion</key><string>${VER}</string>
  <key>CFBundleShortVersionString</key><string>${VER}</string>
  <key>CFBundleExecutable</key><string>Studio Lab</string>
  <key>CFBundleIconFile</key><string>studio-lab</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>LSMinimumSystemVersion</key><string>11.0</string>
  <key>NSHighResolutionCapable</key><true/>
  <key>NSMicrophoneUsageDescription</key><string>Studio Lab does not record audio.</string>
</dict></plist>
PLIST

# self-test: the finished app generates a real song (MP3 through the bundled encoder) before it's packaged
TESTHOME="$PWD/build/testhome"; rm -rf "$TESTHOME"; mkdir -p "$TESTHOME"
STUDIOLAB_NO_FFMPEG=1 HOME="$TESTHOME" "$APP/Contents/MacOS/Studio Lab" generate --style house --length 0.3 --formats mp3 --out "$TESTHOME/out"
ls "$TESTHOME/out"/*.mp3 >/dev/null
echo "app self-test ok"

# ad-hoc signature (no Apple developer ID): required for the bundled Python to run on Apple Silicon
find "$APP" -name __pycache__ -path '*/Resources/app/*' -prune -exec rm -rf {} +
codesign --force --deep --sign - "$APP"
codesign --verify --deep "$APP"

# disk image: the app plus an Applications shortcut to drag it onto
STAGE="build/mac/dmg"; rm -rf "$STAGE"; mkdir -p "$STAGE"
cp -R "$APP" "$STAGE/"
ln -s /Applications "$STAGE/Applications"
# hdiutil sometimes fails with "Resource busy" on CI runners (a disk-image helper still holding the volume): retry
for try in 1 2 3 4 5; do
  if hdiutil create -volname "Studio Lab" -srcfolder "$STAGE" -ov -format UDZO "dist/StudioLab-${VER}-Mac-${LABEL}.dmg"; then
    break
  fi
  [ "$try" = 5 ] && exit 1
  echo "hdiutil busy - retrying in $((try * 10))s"; sleep $((try * 10))
done
echo "built dist/StudioLab-${VER}-Mac-${LABEL}.dmg"
