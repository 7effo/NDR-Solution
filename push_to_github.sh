#!/bin/bash

# Configuration
REMOTE_NAME="NDR-Solution" # Updated to point to NDR-Solution repo
BRANCH_NAME="main"
COMMIT_MSG="ThunderX NDR Update: Phases 1-10 Complete (Logo & Polish)"

# 1. Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
fi

# 2. Add all files
echo "Adding files to staging..."
git add .

# 3. Commit
if git diff-index --quiet HEAD --; then
    echo "No changes to commit."
else
    echo "Committing changes..."
    git commit -m "$COMMIT_MSG"
fi

# 4. Push
echo "Pushing to $REMOTE_NAME/$BRANCH_NAME..."
# Note: This will prompt for username/password if not cached
git push -u $REMOTE_NAME $BRANCH_NAME

echo "✅ Push complete!"
