#!/bin/bash
# Quick script to push to GitHub

REPO_NAME="causal-rationale-extraction-system"
GITHUB_USER="Ritesh-97"

echo "=========================================="
echo "Pushing to GitHub Repository"
echo "=========================================="
echo ""
echo "Repository: $GITHUB_USER/$REPO_NAME"
echo ""
echo "⚠️  You need a Personal Access Token (not password)"
echo "Get one at: https://github.com/settings/tokens"
echo ""
read -sp "Enter your GitHub Personal Access Token: " TOKEN
echo ""

# Remove existing remote if any
git remote remove origin 2>/dev/null

# Add remote with token
git remote add origin "https://$GITHUB_USER:$TOKEN@github.com/$GITHUB_USER/$REPO_NAME.git"

# Push
echo ""
echo "Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed!"
    echo "Repository: https://github.com/$GITHUB_USER/$REPO_NAME"
else
    echo ""
    echo "❌ Push failed. Make sure:"
    echo "1. Repository exists on GitHub (create at https://github.com/new)"
    echo "2. Token has 'repo' scope"
    echo "3. Token is correct"
fi
