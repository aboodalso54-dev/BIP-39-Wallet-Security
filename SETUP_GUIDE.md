# GitHub Actions Setup Guide

This guide explains how to configure your GitHub repository for automatic APK building.

## 1. Enable GitHub Actions

1. Go to your repository on GitHub
2. Click on the **Actions** tab
3. If prompted, click "I understand my workflows, go ahead and enable them"

## 2. Configure Repository Permissions

1. Go to **Settings** > **Actions** > **General**
2. Under **Workflow permissions**, select:
   - ✅ "Read and write permissions"
   - ✅ "Allow GitHub Actions to create and approve pull requests"
3. Click **Save**

## 3. Add Required Secrets

1. Go to **Settings** > **Secrets and variables** > **Actions**
2. Click **New repository secret** for each of the following:

### For Release Builds (Required for signed APKs):

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `KEYSTORE_BASE64` | Output from `base64 -w 0 release.keystore` | Base64 encoded keystore |
| `KEYSTORE_PASSWORD` | `android` | Keystore password |
| `KEY_ALIAS` | `my-key-alias` | Key alias |
| `KEY_PASSWORD` | `android` | Key password |

### Optional Secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `GITHUB_TOKEN` | Automatically provided | No need to set manually |

## 4. Generate Keystore (One-time setup)

Run the provided script to generate a keystore and get the base64 encoded value:

```bash
chmod +x setup-keystore.sh
./setup-keystore.sh
```

**Important**: Save the output securely! You'll need the keystore file and passwords for future app updates.

## 5. Test the Workflows

### Automatic Build (on push):
```bash
git add .
git commit -m "Add GitHub Actions workflows"
git push origin main
```

### Create a Release:
```bash
git tag v1.0.0
git push origin v1.0.0
```

Or manually trigger via GitHub Actions UI.

## 6. Verify Workflow Runs

1. Go to **Actions** tab in your repository
2. Check that workflows run successfully
3. Download APK artifacts from workflow runs
4. For releases, check the **Releases** page for published APKs

## Troubleshooting

### Common Issues:

1. **Permission denied**: Ensure workflow permissions are set to "Read and write"
2. **Keystore not found**: Verify all 4 keystore secrets are added correctly
3. **Gradle failures**: Check that JDK 17 and Node.js 18 are specified in workflow
4. **Artifact upload fails**: Verify `actions/upload-artifact@v4` is used

### Debugging Steps:

1. Check workflow logs in Actions tab
2. Verify secrets are set correctly (values are hidden but existence shows)
3. Test locally with `cd android && ./gradlew assembleRelease`
4. Ensure gradlew is executable (`chmod +x android/gradlew`)

## Workflow Files Overview

- `.github/workflows/android.yml` - CI builds (debug + release for main)
- `.github/workflows/release.yml` - Release builds (signed APKs on tags)
- Both upload APKs as artifacts
- Release workflow creates GitHub Releases with APKs attached