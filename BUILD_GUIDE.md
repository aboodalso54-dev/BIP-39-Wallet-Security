# Quick APK Build Guide

## Option 1: GitHub Actions (Automatic - Recommended)
1. Push this folder to a GitHub repository
2. Go to Actions tab → "Build Android APK" → Run workflow
3. Download APK from Artifacts when complete

## Option 2: Local Build (Run in Terminal)
```bash
# Navigate to workspace
cd "$(pwd)"  # Your workspace path

# Run complete build (installs SDK, builds both projects)
./build_complete.sh
```

## Option 3: Android Studio
1. Open `AndroidAPKProjects/MyApp` in Android Studio
2. Build → Build Bundle(s) / APK(s) → Build APK(s)

## Project Structure
```
AndroidAPKProjects/
├── SimpleApp/          # No-Gradle, SDK tools only
│   └── build_apk.sh    # Builds with aapt2/d8/apksigner
└── MyApp/              # Full Gradle project
    └── gradlew         # Builds with Gradle
```

## APK Features (Both Projects)
- 30+ Android permissions
- Runtime permission requests
- Real-time status checking
- Material Design (MyApp) / Simple UI (SimpleApp)