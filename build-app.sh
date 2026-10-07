#!/data/data/com.termux/files/usr/bin/bash
set -e

cd "$(dirname "$0")"
PROJ_ROOT="$PWD"

export JAVA_HOME="$PREFIX/lib/jvm/java-25-openjdk"
export PATH="$JAVA_HOME/bin:$PATH"
hash -r

SDK="$HOME/android-sdk/platforms/android-36"
FRAMEWORK="/system/framework/framework-res.apk"
OUT="app/build"

rm -rf "$OUT"
mkdir -p "$OUT/res"
mkdir -p "$OUT/classes"
mkdir -p "$OUT/dex"

echo "=== 1. COMPILE RESOURCES ==="
aapt2 compile \
    --dir app/src/main/res \
    -o "$OUT/resources.zip"

echo "=== 2. LINK APK ==="
aapt2 link \
    -o "$OUT/app-unsigned.apk" \
    -I "$FRAMEWORK" \
    --manifest app/src/main/AndroidManifest.xml \
    "$OUT/resources.zip"

echo "=== 3. COMPILE JAVA ==="
javac \
    -source 8 \
    -target 8 \
    -classpath "$SDK/android.jar" \
    -d "$OUT/classes" \
    app/src/main/java/com/quran/app/MainActivity.java \
    app/src/main/java/com/quran/app/AyahActivity.java \
    app/src/main/java/com/quran/app/MushafPageActivity.java \
    app/src/main/java/com/quran/app/MushafTestActivity.java \
    app/src/main/java/com/quran/app/data/MushafPage.java \
    app/src/main/java/com/quran/app/data/MushafPageRepository.java

echo "=== 4. DEX ==="
d8 \
    --lib "$SDK/android.jar" \
    --output "$OUT/dex" \
    $(find "$OUT/classes" -name "*.class")

echo "=== 5. ADD DEX ==="
cd "$OUT"
zip -qj app-unsigned.apk dex/classes.dex

echo "=== 6. ADD ASSETS ==="
( cd "$PROJ_ROOT/app/src/main" && zip -qr "$PROJ_ROOT/$OUT/app-unsigned.apk" assets/ )

echo "=== 7. ALIGN ==="
zipalign -f 4 \
    app-unsigned.apk \
    app-aligned.apk

echo "=== 7. KEY ==="
KEYSTORE="$PROJ_ROOT/debug.keystore"

if [ ! -f "$KEYSTORE" ]; then
    echo "ERROR: Persistent keystore not found: $KEYSTORE"
    exit 1
fi

echo "=== 8. SIGN ==="
apksigner sign \
    --ks "$KEYSTORE" \
    --ks-pass pass:android \
    --key-pass pass:android \
    --out app-debug.apk \
    app-aligned.apk

echo "=== 9. VERIFY ==="
apksigner verify --verbose app-debug.apk

echo
echo "================================"
echo "BUILD SUCCESSFUL"
echo "APK: $PWD/app-debug.apk"
echo "================================"
ls -lh app-debug.apk
