# GitHub Actions Permissions Configuration

This document explains the repository permissions required for the GitHub Actions workflows to function properly.

## Workflow Permissions

Each workflow defines its required permissions explicitly:

### Android CI Workflow (`.github/workflows/android.yml`)
```yaml
permissions:
  contents: read
  packages: write
```

### Android Release Build Workflow (`.github/workflows/release.yml`)
```yaml
permissions:
  contents: write
  packages: write
  id-token: write
```

## Repository Settings

To ensure these workflows work correctly, verify the following repository settings:

1. **Actions Permissions** (Settings > Actions > General):
   - Allow all actions and reusable workflows
   - Allow actions created by GitHub
   - Allow actions by Marketplace verified creators
   - Workflow permissions: "Read and write permissions"
   - Allow GitHub Actions to create and approve pull requests

2. **Repository Secrets** (Settings > Secrets and variables > Actions):
   Add the required secrets for release signing:
   - `KEYSTORE_BASE64`
   - `KEYSTORE_PASSWORD`
   - `KEY_ALIAS`
   - `KEY_PASSWORD`

## Branch Protection Rules (Recommended)

For production repositories, consider setting up branch protection rules:

1. Go to Settings > Branches
2. Add rule for `main` branch:
   - Require status checks to pass before merging
   - Require branches to be up to date before merging
   - Status checks: "build" (from Android CI workflow)
   - Restrict pushes that create files larger than 100MB

## Artifact Retention

Artifacts are configured with retention periods:
- Debug APKs: 7 days
- Release APKs: 30 days

This helps manage storage usage while keeping recent builds accessible.

## Security Considerations

1. **Minimal Permissions**: Each workflow only requests the permissions it needs
2. **Secret Management**: Sensitive data (keystore, passwords) stored as encrypted secrets
3. **Tag-based Releases**: Release workflow only triggers on version tags or manual dispatch
4. **Artifact Expiration**: Automatic cleanup prevents unlimited storage growth