#!/bin/bash
# Automated push script for Citadel Dashboard

set -e

echo "🚀 Citadel Dashboard - Automated Push Script"
echo "============================================"
echo ""

# Check if GitHub CLI is authenticated
if gh auth status &>/dev/null; then
    echo "✅ GitHub CLI is authenticated"
    
    # Check if repo exists
    if gh repo view nisargpatel/citadep-py-dashboard &>/dev/null; then
        echo "✅ Repository exists"
        echo "📤 Pushing code..."
        git push -u origin main
        echo "✅ Successfully pushed!"
    else
        echo "📦 Creating repository..."
        gh repo create citadep-py-dashboard --public --source=. --remote=origin --push
        echo "✅ Repository created and code pushed!"
    fi
else
    echo "❌ GitHub CLI not authenticated"
    echo ""
    echo "Please authenticate first:"
    echo "  1. Run: gh auth login"
    echo "  2. Follow the browser prompts"
    echo "  3. Then run this script again: ./auto-push.sh"
    echo ""
    echo "Or create the repository manually:"
    echo "  1. Go to: https://github.com/new"
    echo "  2. Name: citadep-py-dashboard"
    echo "  3. Make it Public"
    echo "  4. DO NOT initialize with files"
    echo "  5. Then run: git push -u origin main"
    exit 1
fi

echo ""
echo "🎉 Done! View your repo at:"
echo "   https://github.com/nisargpatel/citadep-py-dashboard"
