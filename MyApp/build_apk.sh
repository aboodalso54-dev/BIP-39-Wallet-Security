# Build script for automated APK generation
#!/bin/bash

echo "Building Android APK..."

# Clean previous builds
./gradlew clean

# Build debug APK
./gradlew assembleDebug

# Build release APK (unsigned)
./gradlew assembleRelease

echo "Build complete!"
echo "Debug APK location: app/build/outputs/apk/debug/app-debug.apk"
echo "Release APK location: app/build/outputs/apk/release/app-release-unsigned.apk"

# Optional: Install debug APK to connected device
# ./gradlew installDebug