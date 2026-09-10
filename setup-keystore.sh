#!/bin/bash

# Script to generate keystore and prepare GitHub secrets

echo "🔐 Generating release keystore for Android app signing..."

# Generate keystore
KEYSTORE_PASSWORD="${KEYSTORE_PASSWORD:-android}"
KEY_PASSWORD="${KEY_PASSWORD:-android}"
keytool -genkeypair \
  -v \
  -keystore release.keystore \
  -alias my-key-alias \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000 \
  -storepass "$KEYSTORE_PASSWORD" \
  -keypass "$KEY_PASSWORD" \
  -dname "CN=MyApp, OU=Development, O=MyCompany, L=City, ST=State, C=US"

echo "✅ Keystore generated: release.keystore"

# Encode keystore to base64
KEYSTORE_BASE64=$(base64 -w 0 release.keystore)

echo ""
echo "📋 GitHub Repository Secrets Configuration"
echo "=========================================="
echo ""
echo "Go to your GitHub repository > Settings > Secrets and variables > Actions"
echo "Add the following Repository secrets:"
echo ""
echo "KEYSTORE_BASE64:"
echo "$KEYSTORE_BASE64"
echo ""
echo "KEYSTORE_PASSWORD: android"
echo ""
echo "KEY_ALIAS: my-key-alias"
echo ""
echo "KEY_PASSWORD: android"
echo ""
echo "⚠️  IMPORTANT: Save these values securely! The keystore file and passwords"
echo "   are required for future app updates. Losing them means you cannot"
echo "   update your app on the Play Store."
echo ""
echo "🔒 Store the release.keystore file in a secure location!"
echo "   Consider adding it to your password manager or secure backup."

# Save keystore info to file for reference
cat > keystore-info.txt << EOF
Keystore File: release.keystore
Keystore Password: android
Key Alias: my-key-alias
Key Password: android
Key Algorithm: RSA
Key Size: 2048
Validity: 10000 days

Base64 Encoded Keystore:
$KEYSTORE_BASE64
EOF

echo ""
echo "📄 Keystore information saved to keystore-info.txt"
echo "   (Keep this file secure and do not commit it to version control)"