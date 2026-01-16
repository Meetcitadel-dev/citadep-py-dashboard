#!/bin/bash
# Push script for citadep-py-dashboard

echo "Pushing to GitHub..."

# Remove existing remote if any
git remote remove origin 2>/dev/null

# Add remote (replace YOUR_USERNAME with your GitHub username if different)
git remote add origin https://github.com/nisargpatel/citadep-py-dashboard.git

# Push to GitHub
git push -u origin main

echo "Done! Check https://github.com/nisargpatel/citadep-py-dashboard"
