@echo off
:: Build script for automated APK generation (Windows)

echo Building Android APK...

:: Clean previous builds
gradlew.bat clean

:: Build debug APK
gradlew.bat assembleDebug

:: Build release APK (unsigned)
gradlew.bat assembleRelease

echo Build complete!
echo Debug APK location: app\build\outputs\apk\debug\app-debug.apk
echo Release APK location: app\build\outputs\apk\release\app-release-unsigned.apk

:: Optional: Install debug APK to connected device
:: gradlew.bat installDebug