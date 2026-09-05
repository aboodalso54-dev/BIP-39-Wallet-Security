# Android Permissions Manager App

A complete Android application demonstrating comprehensive permission management with automatic APK building capabilities.

## Features

- Requests and manages all common Android permissions
- Real-time permission status checking
- Material Design UI
- Automated APK build scripts for CI/CD

## Permissions Included

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

## Project Structure

```
MyApp/
├── app/
│   ├── src/main/
│   │   ├── java/com/example/myapp/
│   │   │   └── MainActivity.kt
│   │   ├── res/
│   │   │   ├── layout/activity_main.xml
│   │   │   ├── values/strings.xml, colors.xml, themes.xml
│   │   │   ├── xml/file_paths.xml, backup_rules.xml, data_extraction_rules.xml
│   │   │   ├── drawable/ic_launcher.xml, ic_launcher_round.xml
│   │   │   └── mipmap-*/ic_launcher.xml, ic_launcher_round.xml
│   │   └── AndroidManifest.xml
│   └── build.gradle
├── build.gradle
├── settings.gradle
├── gradle.properties
├── gradlew / gradlew.bat
├── build_apk.sh / build_apk.bat
└── README.md
```

## Building the APK

### Linux/macOS:
```bash
cd MyApp
./build_apk.sh
```

### Windows:
```cmd
cd MyApp
build_apk.bat
```

### Manual Gradle Commands:
```bash
# Clean and build debug APK
./gradlew clean assembleDebug

# Build release APK
./gradlew assembleRelease

# Install to connected device
./gradlew installDebug
```

## Output Locations

- **Debug APK**: `app/build/outputs/apk/debug/app-debug.apk`
- **Release APK**: `app/build/outputs/apk/release/app-release-unsigned.apk`

## Requirements

- JDK 11 or higher
- Android SDK (API 34)
- Gradle 8.1+ (included via wrapper)

## Automatic Permission Handling

The app automatically:
1. Checks current permission status
2. Requests missing permissions at runtime
3. Displays real-time permission states
4. Handles permission results callbacks

## Customization

To modify permissions:
1. Edit `AndroidManifest.xml` - add/remove `<uses-permission>` tags
2. Update `MainActivity.kt` - modify the `permissions` array
3. Rebuild with `./build_apk.sh`

## CI/CD Integration

For GitHub Actions, GitLab CI, or other CI systems:

```yaml
- name: Build APK
  run: |
    chmod +x gradlew
    ./gradlew assembleDebug assembleRelease
    
- name: Upload APK
  uses: actions/upload-artifact@v3
  with:
    name: app-apk
    path: app/build/outputs/apk/
```