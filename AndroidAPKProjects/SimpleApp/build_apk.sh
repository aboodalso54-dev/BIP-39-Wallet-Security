#!/bin/bash
# Simple APK builder using Android SDK tools
# This script builds an APK without requiring Gradle to download dependencies

set -e

echo "Building Simple Android APK..."

# Check for Android SDK
if [ -z "$ANDROID_HOME" ]; then
    export ANDROID_HOME="$HOME/Android/Sdk"
fi

if [ ! -d "$ANDROID_HOME" ]; then
    echo "Android SDK not found at $ANDROID_HOME"
    echo "Please install Android SDK and set ANDROID_HOME"
    exit 1
fi

# Find build tools
BUILD_TOOLS_DIR=$(find "$ANDROID_HOME/build-tools" -maxdepth 1 -type d | sort -V | tail -1)
if [ ! -d "$BUILD_TOOLS_DIR" ]; then
    echo "Android Build Tools not found"
    exit 1
fi

PLATFORM_DIR=$(find "$ANDROID_HOME/platforms" -maxdepth 1 -type d -name "android-*" | sort -V | tail -1)
if [ ! -d "$PLATFORM_DIR" ]; then
    echo "Android Platform not found"
    exit 1
fi

echo "Using Build Tools: $BUILD_TOOLS_DIR"
echo "Using Platform: $PLATFORM_DIR"

# Create output directories
mkdir -p app/build/intermediates
mkdir -p app/build/outputs/apk

# Generate R.java
echo "Generating R.java..."
"$BUILD_TOOLS_DIR/aapt2" compile \
    --dir app/src/main/res \
    -o app/build/intermediates/compiled_res.zip

"$BUILD_TOOLS_DIR/aapt2" link \
    -o app/build/intermediates/base.apk \
    -I "$PLATFORM_DIR/android.jar" \
    --manifest app/src/main/AndroidManifest.xml \
    -R app/build/intermediates/compiled_res.zip \
    --java app/build/intermediates/java \
    --min-sdk-version 24 \
    --target-sdk-version 34

# Compile Java sources
echo "Compiling Java sources..."
mkdir -p app/build/intermediates/classes
javac -source 1.8 -target 1.8 \
    # -bootclasspath "$JAVA_HOME/jmods/java.base.jmod" \
    -classpath "$PLATFORM_DIR/android.jar" \
    -d app/build/intermediates/classes \
    app/src/main/java/com/example/simpleapp/MainActivity.java

# Convert to DEX
echo "Converting to DEX..."
"$BUILD_TOOLS_DIR/d8" \
    --lib "$PLATFORM_DIR/android.jar" \
    --output app/build/intermediates/dex \
    app/build/intermediates/classes/com/example/simpleapp/MainActivity.class

# Package APK
echo "Packaging APK..."
cd app/build/intermediates
"$BUILD_TOOLS_DIR/aapt2" link \
    -o ../../outputs/apk/app-debug.apk \
    -I "$PLATFORM_DIR/android.jar" \
    --manifest ../../../app/src/main/AndroidManifest.xml \
    -R compiled_res.zip \
    --dex dex/classes.dex \
    --min-sdk-version 24 \
    --target-sdk-version 34
cd ../../../

# Sign APK (debug keystore)
echo "Signing APK..."
if [ ! -f ~/.android/debug.keystore ]; then
    keytool -genkey -v -keystore ~/.android/debug.keystore \
        -alias androiddebugkey -keyalg RSA -keysize 2048 -validity 10000 \
        -storepass android -keypass android \
        -dname "CN=Android Debug,O=Android,C=US"
fi

"$BUILD_TOOLS_DIR/apksigner" sign \
    --ks ~/.android/debug.keystore \
    --ks-pass pass:android \
    --key-pass pass:android \
    --out app/build/outputs/app-debug-signed.apk \
    app/build/outputs/apk/app-debug.apk

echo "Build complete!"
echo "Debug APK: app/build/outputs/app-debug-signed.apk"

# Verify APK
"$BUILD_TOOLS_DIR/aapt2" dump badging app/build/outputs/app-debug-signed.apk | head -20