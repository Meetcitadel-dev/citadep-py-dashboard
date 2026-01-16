#!/bin/bash
# Complete push script with authentication handling

echo "🚀 Pushing Citadel Dashboard to GitHub..."
echo ""

# Check if repo exists
REPO_URL="https://github.com/nisargpatel/citadep-py-dashboard.git"
echo "Repository: $REPO_URL"
echo ""

# Set remote
git remote remove origin 2>/dev/null
git remote add origin "$REPO_URL"

# Try to push
echo "Attempting to push..."
if git push -u origin main 2>&1; then
    echo "✅ Successfully pushed to GitHub!"
    echo "View at: https://github.com/nisargpatel/citadep-py-dashboard"
else
    echo ""
    echo "❌ Push failed. This usually means:"
    echo "   1. Repository doesn't exist yet - create it at https://github.com/new"
    echo "   2. Authentication required - GitHub will prompt for credentials"
    echo ""
    echo "If prompted, enter your GitHub username and a Personal Access Token"
    echo "Create token at: https://github.com/settings/tokens"
    echo ""
    echo "Or authenticate GitHub CLI:"
    echo "   gh auth login"
    echo "   Then run: gh repo create citadep-py-dashboard --public --source=. --remote=origin --push"
fi
