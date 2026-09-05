#!/bin/bash
# Complete Android APK Build Script
# Run this in your terminal to build the APK

set -e

WORKSPACE="/workspace/ef3666c6-a0dc-4dbb-a42b-97317fc721b3/sessions/agent_15cb467b-9d12-48d3-954f-dff0f2d58b09"
PROJECT_DIR="$WORKSPACE/AndroidAPKProjects/SimpleApp"

echo "=== Building Android APK ==="

# 1. Install Android SDK if not present
if [ ! -d "$WORKSPACE/Android/Sdk/cmdline-tools/latest/bin" ]; then
    echo "Installing Android SDK..."
    mkdir -p "$WORKSPACE/Android/Sdk"
    cd "$WORKSPACE/Android/Sdk"
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip -O cmdline-tools.zip
    unzip -q cmdline-tools.zip
    mkdir -p cmdline-tools/latest
    mv cmdline-tools/* cmdline-tools/latest/ 2>/dev/null || true
    rm cmdline-tools.zip
fi

# 2. Set environment
export ANDROID_HOME="$WORKSPACE/Android/Sdk"
export PATH="$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools"

# 3. Install build components
echo "Installing build tools..."
yes | sdkmanager --licenses > /dev/null 2>&1
sdkmanager "build-tools;34.0.0" "platforms;android-34" "platform-tools" > /dev/null 2>&1

# 4. Build APK
echo "Building APK..."
cd "$PROJECT_DIR"
chmod +x build_apk.sh
./build_apk.sh

# 5. Verify
APK_PATH="$PROJECT_DIR/app/build/outputs/app-debug-signed.apk"
if [ -f "$APK_PATH" ]; then
    echo "=== BUILD SUCCESS ==="
    echo "APK Location: $APK_PATH"
    echo "APK Size: $(du -h "$APK_PATH" | cut -f1)"
    echo ""
    echo "To install on device:"
    echo "  adb install -r \"$APK_PATH\""
else
    echo "=== BUILD FAILED ==="
    echo "APK not found at: $APK_PATH"
    exit 1
fi