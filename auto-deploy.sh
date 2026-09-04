#!/bin/bash

# Auto-deploy script for GitHub Repository with Actions
# Usage: ./auto-deploy.sh [repo-name] [--private]

set -e

REPO_NAME="${1:-myapp}"
VISIBILITY="${2:-public}"

echo "🚀 Starting auto-deployment for: $REPO_NAME ($VISIBILITY)"
echo "=================================================="

# Check if gh is authenticated
if ! gh auth status >/dev/null 2>&1; then
    echo "🔐 GitHub CLI not authenticated. Please run:"
    echo "   gh auth login"
    exit 1
fi

echo "✅ GitHub CLI authenticated"

# Get current user
GH_USER=$(gh api user --jq '.login')
echo "👤 GitHub user: $GH_USER"

# Check if we can create repos
echo "🔍 Checking repository creation permissions..."
if gh api user/repos --jq '.[0].name' >/dev/null 2>&1; then
    CAN_CREATE=true
else
    CAN_CREATE=false
    echo "⚠️  Cannot create repositories with current token"
fi

# Create repository if possible
if [ "$CAN_CREATE" = true ]; then
    echo "📦 Creating repository: $GH_USER/$REPO_NAME"
    if gh repo view "$GH_USER/$REPO_NAME" >/dev/null 2>&1; then
        echo "⚠️  Repository already exists"
    else
        gh repo create "$REPO_NAME" --"$VISIBILITY" --description "React Native Android App with Auto APK Build" --disable-wiki --disable-issues || {
            echo "❌ Failed to create repository. You may need to create it manually."
            CAN_CREATE=false
        }
    fi
else
    echo "📋 Repository creation skipped (insufficient permissions)"
    echo "   Please create repository manually at: https://github.com/new"
    echo "   Repository name: $REPO_NAME"
    read -p "Press Enter after creating repository..."
fi

# Initialize git if needed
if [ ! -d ".git" ] || [ ! "$(git rev-parse --is-inside-work-tree 2>/dev/null)" = "true" ]; then
    echo "🔧 Initializing git repository"
    git init
    git add .
    git commit -m "Initial commit: React Native app with GitHub Actions for APK building"
fi

# Add remote and push
echo "🔗 Setting up remote and pushing code"
git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/$GH_USER/$REPO_NAME.git"
git branch -M main

# Try push, if repo doesn't exist yet, user needs to create it
if ! git push -u origin main --force 2>/dev/null; then
    echo "❌ Push failed. Repository may not exist yet."
    echo "   Please create it at: https://github.com/new"
    echo "   Name: $REPO_NAME"
    read -p "Press Enter after creating repository, then I'll retry push..."
    git push -u origin main --force
fi
echo "✅ Code pushed to GitHub"

# Generate keystore if not exists
if [ ! -f "release.keystore" ]; then
    echo "🔐 Generating release keystore"
    ./setup-keystore.sh
fi

# Extract keystore info
KEYSTORE_BASE64=$(base64 -w 0 release.keystore 2>/dev/null || base64 release.keystore)
KEYSTORE_PASSWORD="android"
KEY_ALIAS="my-key-alias"
KEY_PASSWORD="android"

# Add repository secrets (requires admin access)
echo "🔑 Adding repository secrets"
if gh secret set KEYSTORE_BASE64 --body "$KEYSTORE_BASE64" --repo "$GH_USER/$REPO_NAME" 2>/dev/null; then
    gh secret set KEYSTORE_PASSWORD --body "$KEYSTORE_PASSWORD" --repo "$GH_USER/$REPO_NAME"
    gh secret set KEY_ALIAS --body "$KEY_ALIAS" --repo "$GH_USER/$REPO_NAME"
    gh secret set KEY_PASSWORD --body "$KEY_PASSWORD" --repo "$GH_USER/$REPO_NAME"
    echo "✅ Secrets added"
else
    echo "⚠️  Cannot add secrets automatically (insufficient permissions)"
    echo "   Please add these manually in GitHub:"
    echo "   Repository > Settings > Secrets and variables > Actions > New repository secret"
    echo ""
    echo "   KEYSTORE_BASE64: $KEYSTORE_BASE64"
    echo "   KEYSTORE_PASSWORD: $KEYSTORE_PASSWORD"
    echo "   KEY_ALIAS: $KEY_ALIAS"
    echo "   KEY_PASSWORD: $KEY_PASSWORD"
fi

# Try to configure Actions permissions
echo "⚙️  Configuring Actions permissions"
if gh api --method PUT "repos/$GH_USER/$REPO_NAME/actions/permissions" \
  -f enabled=true -f allowed_actions=all >/dev/null 2>&1; then
    
  gh api --method PUT "repos/$GH_USER/$REPO_NAME/actions/permissions/workflow" \
    -f default_workflow_permissions=write -f can_approve_pull_request_reviews=true >/dev/null
  echo "✅ Actions configured"
else
    echo "⚠️  Cannot configure Actions permissions automatically"
    echo "   Please enable manually:"
    echo "   Repository > Settings > Actions > General >"
    echo "   - Allow all actions ✓"
    echo "   - Workflow permissions: Read and write ✓"
fi

# Trigger first workflow run
echo "🏃 Triggering first workflow run"
if gh workflow run android.yml --repo "$GH_USER/$REPO_NAME" --ref main 2>/dev/null; then
    echo "✅ Workflow triggered"
else
    echo "⚠️  Could not trigger workflow automatically"
    echo "   It will run automatically on next push"
fi

# Summary
echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "======================"
echo "📱 Repository: https://github.com/$GH_USER/$REPO_NAME"
echo "⚡ Actions: https://github.com/$GH_USER/$REPO_NAME/actions"
echo "📦 Releases: https://github.com/$GH_USER/$REPO_NAME/releases"
echo ""
echo "🔗 After build completes:"
echo "   Debug APK: Actions > Latest run > Artifacts > debug-apk"
echo "   Release APK: Create tag (git tag v1.0.0 && git push origin v1.0.0)"
echo ""
echo "📋 To create a release:"
echo "   git tag v1.0.0 && git push origin v1.0.0"
echo ""
echo "🔐 Keystore info saved in: keystore-info.txt (KEEP SECURE!)"