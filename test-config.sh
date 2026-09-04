#!/bin/bash

# Test script to validate Android build configuration

echo "🧪 Testing Android build configuration..."

# Check if gradlew exists and is executable
if [ ! -f "android/gradlew" ]; then
    echo "❌ android/gradlew not found"
    exit 1
fi

if [ ! -x "android/gradlew" ]; then
    echo "⚠️  android/gradlew not executable, fixing..."
    chmod +x android/gradlew
fi

echo "✅ gradlew found and executable"

# Check required files
REQUIRED_FILES=(
    "android/settings.gradle"
    "android/build.gradle"
    "android/app/build.gradle"
    "android/app/src/main/AndroidManifest.xml"
    "android/app/src/main/java/com/example/myapp/MainApplication.java"
    "android/app/src/main/java/com/example/myapp/MainActivity.java"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing required file: $file"
        exit 1
    fi
done

echo "✅ All required Android files present"

# Check package.json
if [ ! -f "package.json" ]; then
    echo "❌ package.json not found"
    exit 1
fi

echo "✅ package.json found"

# Check workflow files
WORKFLOW_FILES=(
    ".github/workflows/android.yml"
    ".github/workflows/release.yml"
)

for file in "${WORKFLOW_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing workflow file: $file"
        exit 1
    fi
done

echo "✅ All workflow files present"

# Validate gradle files have basic structure
if ! grep -q "com.android.application" android/app/build.gradle; then
    echo "❌ android/app/build.gradle missing Android application plugin"
    exit 1
fi

if ! grep -q "react-native" android/app/build.gradle; then
    echo "❌ android/app/build.gradle missing React Native dependency"
    exit 1
fi

echo "✅ Gradle configuration looks correct"

echo ""
echo "🎉 All checks passed! Configuration appears valid."
echo ""
echo "Next steps:"
echo "1. Run './setup-keystore.sh' to generate signing keystore"
echo "2. Add secrets to GitHub repository (see SETUP_GUIDE.md)"
echo "3. Push to GitHub to trigger workflows"
echo "4. Check Actions tab for build results"