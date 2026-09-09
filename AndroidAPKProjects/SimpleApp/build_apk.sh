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
mkdir -p app/build/deps/jars

# Download required AndroidX AARs and extract classes.jar
# (This keeps the simple non-Gradle build working by pulling runtime classes)
DEPS_DIR=app/build/deps
declare -A AARS
AARS[core]=1.12.0
AARS[appcompat]=1.6.1

MAVEN_BASE="https://repo1.maven.org/maven2/androidx"

for name in "${!AARS[@]}"; do
    ver=${AARS[$name]}
    aar_path="$DEPS_DIR/${name}-${ver}.aar"
    url="$MAVEN_BASE/$name/$name/$ver/$name-$ver.aar"
    echo "Downloading $name:$ver from $url"
    curl -fL -o "$aar_path" "$url"
    unpack_dir="$DEPS_DIR/${name}_unpack"
    mkdir -p "$unpack_dir"
    unzip -o "$aar_path" -d "$unpack_dir"
    if [ -f "$unpack_dir/classes.jar" ]; then
        cp "$unpack_dir/classes.jar" "$DEPS_DIR/jars/${name}.jar"
    fi
    # copy any jars in libs folder
    if [ -d "$unpack_dir/libs" ]; then
        for j in "$unpack_dir/libs"/*.jar; do
            [ -e "$j" ] || continue
            base=$(basename "$j")
            cp "$j" "$DEPS_DIR/jars/${name}_$base"
        done
    fi
done

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
    --target-sdk-version 34 \
    --auto-add-overlay

# Compile Java sources (including generated R.java)
echo "Compiling Java sources..."
mkdir -p app/build/intermediates/classes

# Build classpath: android.jar + downloaded jars + generated java folder
CP="$PLATFORM_DIR/android.jar:$DEPS_DIR/jars/*:app/build/intermediates/java"

# Collect java source files from main and generated java
JAVA_SOURCES=$(find app/src/main/java app/build/intermediates/java -name "*.java" -print)
if [ -z "$JAVA_SOURCES" ]; then
    echo "No Java sources found to compile"
    exit 1
fi

javac -source 1.8 -target 1.8 \
    -classpath "$CP" \
    -d app/build/intermediates/classes \
    $JAVA_SOURCES

# Convert to DEX
echo "Converting to DEX..."
mkdir -p app/build/intermediates/dex

# Pass the compiled classes directory and dependency jars to d8
"$BUILD_TOOLS_DIR/d8" \
    --lib "$PLATFORM_DIR/android.jar" \
    --output app/build/intermediates/dex \
    app/build/intermediates/classes \
    $DEPS_DIR/jars/*

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
    --target-sdk-version 34 \
    --auto-add-overlay
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
