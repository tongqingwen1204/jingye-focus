#!/usr/bin/env bash
# 不依赖 Gradle / Android Studio 的打包脚本：aapt2 -> javac -> d8 -> zipalign -> apksigner
# 用法：ANDROID_HOME=/path/to/sdk ./build_apk.sh
set -euo pipefail

SDK="${ANDROID_HOME:-/root/android-sdk}"
BUILD_TOOLS="${BUILD_TOOLS:-$SDK/build-tools/35.0.0}"
PLATFORM="${PLATFORM:-$SDK/platforms/android-35/android.jar}"
ROOT="$(cd "$(dirname "$0")" && pwd)"
OUT="$ROOT/build-manual"
APP_ID="com.jingye.focus"
VERSION_CODE=1
VERSION_NAME="1.0"

echo "==> 清理"
rm -rf "$OUT"
mkdir -p "$OUT/res" "$OUT/gen" "$OUT/classes" "$OUT/dex" "$OUT/manifest" "$ROOT/dist"

echo "==> 注入 package 的 manifest（Gradle 工程里由 namespace 提供）"
sed "s|<manifest xmlns:android=\"http://schemas.android.com/apk/res/android\">|<manifest xmlns:android=\"http://schemas.android.com/apk/res/android\" package=\"$APP_ID\">|" \
  "$ROOT/app/src/main/AndroidManifest.xml" > "$OUT/manifest/AndroidManifest.xml"

echo "==> 编译资源"
"$BUILD_TOOLS/aapt2" compile --dir "$ROOT/app/src/main/res" -o "$OUT/res/resources.zip"

echo "==> 链接资源"
"$BUILD_TOOLS/aapt2" link \
  -o "$OUT/base.apk" \
  -I "$PLATFORM" \
  --manifest "$OUT/manifest/AndroidManifest.xml" \
  -R "$OUT/res/resources.zip" \
  --java "$OUT/gen" \
  --min-sdk-version 29 \
  --target-sdk-version 34 \
  --version-code "$VERSION_CODE" \
  --version-name "$VERSION_NAME" \
  --auto-add-overlay

echo "==> 编译 Java"
find "$ROOT/app/src/main/java" "$OUT/gen" -name '*.java' > "$OUT/sources.txt"
javac -encoding UTF-8 -source 11 -target 11 -classpath "$PLATFORM" \
  -d "$OUT/classes" @"$OUT/sources.txt"

echo "==> dex"
find "$OUT/classes" -name '*.class' > "$OUT/classes.txt"
"$BUILD_TOOLS/d8" --lib "$PLATFORM" --min-api 29 --output "$OUT/dex" @"$OUT/classes.txt"

echo "==> 打包 dex"
cp "$OUT/base.apk" "$OUT/unsigned.apk"
(cd "$OUT/dex" && zip -q -X "$OUT/unsigned.apk" classes.dex)

echo "==> 对齐 + 签名"
"$BUILD_TOOLS/zipalign" -f 4 "$OUT/unsigned.apk" "$OUT/aligned.apk"
if [ ! -f "$ROOT/keystore.jks" ]; then
  keytool -genkeypair -keystore "$ROOT/keystore.jks" -alias focus \
    -keyalg RSA -keysize 2048 -validity 10000 \
    -storepass android -keypass android \
    -dname "CN=JingYe Focus, OU=Personal, O=JingYe, L=Shanghai, C=CN"
fi
"$BUILD_TOOLS/apksigner" sign \
  --ks "$ROOT/keystore.jks" --ks-pass pass:android --key-pass pass:android \
  --min-sdk-version 29 \
  --v1-signing-enabled true --v2-signing-enabled true --v3-signing-enabled true \
  --out "$ROOT/dist/jingye-focus-1.0.apk" "$OUT/aligned.apk"

echo "==> 校验"
"$BUILD_TOOLS/apksigner" verify --print-certs "$ROOT/dist/jingye-focus-1.0.apk" | head -4
ls -lh "$ROOT/dist/jingye-focus-1.0.apk"
