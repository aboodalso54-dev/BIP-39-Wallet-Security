#!/bin/bash

# Interactive deployment guide - runs locally on your machine
# This script provides step-by-step commands you can copy-paste

REPO_NAME="${1:-myapp}"
VISIBILITY="${2:-public}"

echo "🚀 GitHub Repository Deployment Guide"
echo "====================================="
echo ""
echo "This script generates exact commands for you to run locally."
echo "Repository: $REPO_NAME ($VISIBILITY)"
echo ""

# Generate keystore first
if [ ! -f "release.keystore" ]; then
    echo "🔐 Step 0: Generate keystore (run once locally)"
    echo "----------------------------------------"
    echo "./setup-keystore.sh"
    echo ""
fi

echo "📋 Step 1: Create GitHub Repository"
echo "-----------------------------------"
echo "# Go to: https://github.com/new"
echo "# Repository name: $REPO_NAME"
echo "# Visibility: $VISIBILITY"
echo "# DON'T initialize README, .gitignore, or license"
echo "# Click 'Create repository'"
echo ""

echo "📋 Step 2: Push Code (run these commands locally)"
echo "------------------------------------------------"
echo "git init"
echo "git add ."
echo "git commit -m \"Initial commit: React Native app with GitHub Actions for APK building\""
echo "git branch -M main"
echo "git remote add origin https://github.com/YOUR_USERNAME/$REPO_NAME.git"
echo "git push -u origin main"
echo ""

echo "📋 Step 3: Add Secrets (copy values from keystore-info.txt)"
echo "-----------------------------------------------------------"
if [ -f "keystore-info.txt" ]; then
    KEYSTORE_BASE64=$(grep -A 1 "Base64 Encoded Keystore:" keystore-info.txt | tail -1)
    echo "# Go to: https://github.com/YOUR_USERNAME/$REPO_NAME/settings/secrets/actions"
    echo "# Click 'New repository secret' for each:"
    echo ""
    echo "Secret: KEYSTORE_BASE64"
    echo "Value:  $KEYSTORE_BASE64"
    echo ""
    echo "Secret: KEYSTORE_PASSWORD"
    echo "Value:  android"
    echo ""
    echo "Secret: KEY_ALIAS"
    echo "Value:  my-key-alias"
    echo ""
    echo "Secret: KEY_PASSWORD"
    echo "Value:  android"
else
    echo "# Run ./setup-keystore.sh first, then add secrets from keystore-info.txt"
fi
echo ""

echo "📋 Step 4: Enable Actions Permissions"
echo "-------------------------------------"
echo "# Go to: https://github.com/YOUR_USERNAME/$REPO_NAME/settings/actions"
echo "# Under 'Actions permissions':"
echo "#   ✓ Allow all actions and reusable workflows"
echo "# Under 'Workflow permissions':"
echo "#   ✓ Read and write permissions"
echo "#   ✓ Allow GitHub Actions to create and approve pull requests"
echo "# Click Save"
echo ""

echo "📋 Step 5: Trigger First Build"
echo "------------------------------"
echo "# Option A: Push any commit (automatic)"
echo "git commit --allow-empty -m \"Trigger CI\" && git push"
echo ""
echo "# Option B: Manual trigger via GitHub CLI (if authenticated)"
echo "gh workflow run android.yml --repo YOUR_USERNAME/$REPO_NAME --ref main"
echo ""

echo "📋 Step 6: Create Release (when ready)"
echo "--------------------------------------"
echo "git tag v1.0.0"
echo "git push origin v1.0.0"
echo ""
echo "# This triggers release.yml workflow"
echo "# Check: https://github.com/YOUR_USERNAME/$REPO_NAME/releases"
echo ""

echo "🔗 Important URLs (replace YOUR_USERNAME):"
echo "   Repository: https://github.com/YOUR_USERNAME/$REPO_NAME"
echo "   Actions:    https://github.com/YOUR_USERNAME/$REPO_NAME/actions"
echo "   Releases:   https://github.com/YOUR_USERNAME/$REPO_NAME/releases"
echo "   Settings:   https://github.com/YOUR_USERNAME/$REPO_NAME/settings"
echo ""

echo "📱 Download Links (after builds complete):"
echo "   Debug APK:  Actions > Run > Artifacts > debug-apk"
echo "   Release:    Releases > v1.0.0 > Assets > app-release.apk"
echo "   Direct:     https://github.com/YOUR_USERNAME/$REPO_NAME/releases/download/v1.0.0/app-release.apk"
echo ""

echo "⚠️  IMPORTANT: Save keystore-info.txt securely!"
echo "   You need it for ALL future app updates."
echo "   Losing it = cannot update app on Play Store."