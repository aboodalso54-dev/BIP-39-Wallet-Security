#!/bin/bash
# Complete Build Script - Run this in your terminal

set -e

WORKSPACE="/workspace/ef3666c6-a0dc-4dbb-a42b-97317fc721b3/sessions/agent_15cb467b-9d12-48d3-954f-dff0f2d58b09"

echo "=== Complete Android APK Build ==="

# 1. Install Android SDK
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

# 3. Install components
echo "Installing build tools..."
yes | sdkmanager --licenses > /dev/null 2>&1
sdkmanager "build-tools;34.0.0" "platforms;android-34" "platform-tools" > /dev/null 2>&1

# 4. Build SimpleApp (SDK tools)
echo "Building SimpleApp..."
cd "$WORKSPACE/AndroidAPKProjects/SimpleApp"
chmod +x build_apk.sh
./build_apk.sh

# 5. Build MyApp (Gradle)
echo "Building MyApp..."
cd "$WORKSPACE/AndroidAPKProjects/MyApp"
chmod +x gradlew
./gradlew assembleDebug

# 6. Results
echo ""
echo "=== BUILD COMPLETE ==="
echo "SimpleApp APK: $WORKSPACE/AndroidAPKProjects/SimpleApp/app/build/outputs/app-debug-signed.apk"
echo "MyApp APK:     $WORKSPACE/AndroidAPKProjects/MyApp/app/build/outputs/apk/debug/app-debug.apk"
echo ""
ls -la "$WORKSPACE/AndroidAPKProjects/SimpleApp/app/build/outputs/app-debug-signed.apk" 2>/dev/null || echo "SimpleApp APK not found"
ls -la "$WORKSPACE/AndroidAPKProjects/MyApp/app/build/outputs/apk/debug/app-debug.apk" 2>/dev/null || echo "MyApp APK not found"