# MyApp - React Native Android App

This is a React Native application configured with GitHub Actions for automatic APK building.

## GitHub Actions Workflows

This project includes two GitHub Actions workflows:

1. **Android CI** (`.github/workflows/android.yml`) - Runs on every push and pull request
   - Builds debug APK for testing
   - Builds release APK for main branch pushes
   - Uploads artifacts for download

2. **Android Release Build** (`.github/workflows/release.yml`) - Runs on version tags (v*)
   - Builds signed release APK
   - Creates GitHub Release with APK attached
   - Can be triggered manually with version input

## Required Repository Secrets

For the release workflow to work properly, you need to configure the following secrets in your GitHub repository settings:

### For Signed Releases:
1. Go to your repository on GitHub
2. Navigate to Settings > Secrets and variables > Actions
3. Add the following repository secrets:

| Secret Name | Description |
|-------------|-------------|
| `KEYSTORE_BASE64` | Base64 encoded keystore file (generate with `base64 -w 0 release.keystore`) |
| `KEYSTORE_PASSWORD` | Keystore password |
| `KEY_ALIAS` | Key alias |
| `KEY_PASSWORD` | Key password |

### Generating a Keystore:
```bash
keytool -genkeypair -v -keystore release.keystore -alias my-key-alias -keyalg RSA -keysize 2048 -validity 10000
```

Then encode it:
```bash
base64 -w 0 release.keystore
```

## Repository Permissions

The workflows require the following permissions which are set in the workflow files:

- `contents: read` - For checking out code
- `contents: write` - For creating releases (release workflow only)
- `packages: write` - For uploading artifacts
- `id-token: write` - For OIDC tokens if needed

These permissions are configured in each workflow file under the `permissions` key.

## Building Locally

### Prerequisites:
- Node.js 18+
- JDK 17+
- Android Studio with SDK 34

### Steps:
```bash
# Install dependencies
npm install

# Build debug APK
cd android && ./gradlew assembleDebug

# Build release APK (requires keystore configuration)
cd android && ./gradlew assembleRelease
```

## APK Locations

- Debug APK: `android/app/build/outputs/apk/debug/app-debug.apk`
- Release APK: `android/app/build/outputs/apk/release/app-release.apk`

## Triggering Releases

### Automatic (on tag push):
```bash
git tag v1.0.0
git push origin v1.0.0
```

### Manual (via GitHub UI):
1. Go to Actions tab
2. Select "Android Release Build" workflow
3. Click "Run workflow"
4. Enter version tag (e.g., v1.0.0)
5. Click "Run workflow"