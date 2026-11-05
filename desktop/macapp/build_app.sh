#!/bin/bash
# 🐒 大肥猴 .app 打包脚本
# 用系统 python3（PyObjC 装在系统 site-packages，不在 venv 里）
set -e

ROOT="/Users/zmz/.openclaw/workspace/da-fei-hou"
MACAPP="$ROOT/desktop/macapp"
DIST="$MACAPP/dist"
APP="$DIST/大肥猴.app"
PY="$(command -v python3)"

echo "🐒 打包大肥猴.app (python: $PY)"

# 确认系统 python 能用 PyObjC
if ! "$PY" -c "import objc, AppKit" 2>/dev/null; then
  echo "❌ 系统 python 缺 PyObjC，请先： $PY -m pip install pyobjc-core pyobjc-framework-Cocoa pyobjc-framework-Quartz"
  exit 1
fi

rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources/assets"

cp -R "$ROOT/assets/sprites_transparent" "$APP/Contents/Resources/assets/"
cp -R "$ROOT/assets/voice" "$APP/Contents/Resources/assets/"
cp "$ROOT/desktop/native/da_fei_hou.py" "$APP/Contents/Resources/da_fei_hou.py"

# 图标
if [ -f "$ROOT/assets/sprites_transparent/idle.png" ]; then
  ICONSET="$(mktemp -d)/icon.iconset"
  mkdir -p "$ICONSET"
  for s in 16 32 64 128 256 512; do
    sips -z $s $s "$ROOT/assets/sprites_transparent/idle.png" --out "$ICONSET/icon_${s}x${s}.png" >/dev/null 2>&1 || true
  done
  cp "$ICONSET/icon_512x512.png" "$ICONSET/icon_512x512@2x.png" 2>/dev/null || true
  iconutil -c icns "$ICONSET" -o "$APP/Contents/Resources/icon.icns" 2>/dev/null || echo "  (图标跳过)"
fi

# 启动器
cat > "$APP/Contents/MacOS/大肥猴" << 'LAUNCHEOF'
#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
RES="$DIR/../Resources"
exec "__PYTHON__" "$RES/da_fei_hou.py" "$@"
LAUNCHEOF
sed -i '' "s|__PYTHON__|$PY|" "$APP/Contents/MacOS/大肥猴"
chmod +x "$APP/Contents/MacOS/大肥猴"

# Info.plist
cat > "$APP/Contents/Info.plist" << 'PLISTEOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key><string>大肥猴</string>
  <key>CFBundleDisplayName</key><string>大肥猴</string>
  <key>CFBundleIdentifier</key><string>com.openclaw.dafeihou</string>
  <key>CFBundleExecutable</key><string>大肥猴</string>
  <key>CFBundleIconFile</key><string>icon</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>0.1.0</string>
  <key>CFBundleVersion</key><string>0.1.0</string>
  <key>LSUIElement</key><true/>
  <key>NSHighResolutionCapable</key><true/>
  <key>LSMinimumSystemVersion</key><string>12.0</string>
</dict>
</plist>
PLISTEOF

printf 'APPL????' > "$APP/Contents/PkgInfo"

codesign --force --deep --sign - "$APP" 2>/dev/null || echo "  (签名跳过)"

echo "✅ 打包完成: $APP"
du -sh "$APP"
