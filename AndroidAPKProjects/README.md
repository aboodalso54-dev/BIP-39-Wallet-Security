# Android APK Building Projects

This repository contains two complete Android projects for building APKs with comprehensive permission management:

## Projects

### 1. MyApp - Full Gradle Project
Complete Android Studio/Gradle project with modern build system.

**Features:**
- Kotlin-based with modern Android architecture
- Material Design UI
- Comprehensive permission management (26 permissions)
- Gradle build system with release/debug variants
- CI/CD ready configuration
- ProGuard support

**Building:**
```bash
cd MyApp
./gradlew clean assembleDebug assembleRelease
# Or use the build script
./build_apk.sh
```

**Output:**
- Debug: `app/build/outputs/apk/debug/app-debug.apk`
- Release: `app/build/outputs/apk/release/app-release-unsigned.apk`

### 2. SimpleApp - Minimal SDK Tools Project
Lightweight project using only Android SDK command-line tools (no Gradle).

**Features:**
- Pure Java implementation
- No external dependencies
- Builds with aapt2, d8, apksigner directly
- Single build script
- Minimal footprint

**Building:**
```bash
cd SimpleApp
./build_apk.sh
```

**Requirements:**
- Android SDK (Build Tools + Platform API 34)
- Java 8+
- ANDROID_HOME set

**Output:**
- Signed Debug: `app/build/outputs/app-debug-signed.apk`

## Permissions Included (Both Projects)

- Internet & Network access
- Phone state & SMS
- Location (Fine & Coarse)
- Camera & Audio recording
- Storage (Read/Write)
- Bluetooth & NFC
- System settings & Overlay
- Foreground services
- Package installation
- Usage stats

## Quick Start

### For Development (Recommended)
Use **MyApp** with Android Studio:
1. Open `MyApp` folder in Android Studio
2. Let Gradle sync
3. Build → Build Bundle(s) / APK(s) → Build APK(s)

### For Automated/CI Builds
Use **SimpleApp** with build script:
1. Ensure Android SDK is installed
2. Set ANDROID_HOME environment variable
3. Run `./build_apk.sh`

## Customization

Both projects support easy permission customization:

1. **AndroidManifest.xml** - Add/remove `<uses-permission>` tags
2. **MainActivity** - Update permissions array
3. **Rebuild** with respective build commands

## CI/CD Integration

### GitHub Actions (MyApp)
```yaml
- name: Build APK
  run: |
    chmod +x gradlew
    ./gradlew assembleDebug assembleRelease
```

### GitHub Actions (SimpleApp)
```yaml
- name: Setup Android SDK
  uses: android-actions/setup-android@v2
  
- name: Build APK
  run: |
    cd SimpleApp
    ./build_apk.sh
```

## License

MIT License - Feel free to use for learning or production.

## Support

For issues with:
- **MyApp**: Check Gradle/Android Studio setup
- **SimpleApp**: Verify Android SDK installation and ANDROID_HOME