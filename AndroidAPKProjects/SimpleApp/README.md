# Simple Android Permissions Manager

A minimal Android application demonstrating comprehensive permission management, built without Gradle dependencies.

## Features

- Requests and manages 26 common Android permissions
- Real-time permission status checking
- Built with pure Android SDK tools (no Gradle required)
- Automatic APK building script

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
SimpleApp/
├── app/
│   ├── src/main/
│   │   ├── java/com/example/simpleapp/
│   │   │   └── MainActivity.java
│   │   ├── res/
│   │   │   ├── layout/activity_main.xml
│   │   │   ├── values/strings.xml
│   │   │   ├── xml/file_paths.xml
│   │   │   └── drawable/ic_launcher.xml
│   │   └── AndroidManifest.xml
├── build_apk.sh
└── README.md
```

## Building the APK

### Prerequisites

1. **Android SDK** installed with:
   - Build Tools (latest)
   - Platform SDK (API 34)
2. **Java 8+** installed
3. **ANDROID_HOME** environment variable set

### Build Command

```bash
cd SimpleApp
./build_apk.sh
```

### Output

- **Signed Debug APK**: `app/build/outputs/app-debug-signed.apk`

## Requirements

- Android SDK (Build Tools + Platform API 34)
- Java 8 or higher
- Linux/macOS (Windows users can use WSL)

## Automatic Permission Handling

The app automatically:
1. Checks current permission status
2. Requests missing permissions at runtime
3. Displays real-time permission states with ✅/❌ indicators
4. Handles permission results callbacks

## Customization

To modify permissions:
1. Edit `app/src/main/AndroidManifest.xml` - add/remove `<uses-permission>` tags
2. Update `MainActivity.java` - modify the `permissions` array
3. Rebuild with `./build_apk.sh`

## Installation

```bash
# Install to connected device
adb install -r app/build/outputs/app-debug-signed.apk

# Or transfer APK to device and install manually
```

## Note

This is a simplified build system for demonstration. For production apps, use Android Studio with Gradle for proper dependency management, resource optimization, and build variants.