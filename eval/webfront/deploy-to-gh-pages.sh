#!/bin/bash

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting GitHub Pages Deployment...${NC}"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}Error: git is not installed. Please install git first.${NC}"
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree &> /dev/null; then
    echo -e "${RED}Error: Not in a git repository. Please run this script from within a git repository.${NC}"
    exit 1
fi

# Save current branch name and repository root
CURRENT_BRANCH=$(git symbolic-ref --short HEAD)
REPO_ROOT=$(git rev-parse --show-toplevel)
echo -e "Current branch: ${YELLOW}$CURRENT_BRANCH${NC}"

# Get remote repository information
REPO_URL=$(git config --get remote.origin.url)
REPO_NAME=$(basename -s .git "$REPO_URL")

# Source directory containing web files
SRC_DIR="$REPO_ROOT/eval/webfront"
if [ ! -d "$SRC_DIR" ]; then
    echo -e "${RED}Error: Source directory $SRC_DIR does not exist.${NC}"
    exit 1
fi

# Create a temporary directory for deployment
TEMP_DIR=$(mktemp -d)
echo -e "${YELLOW}Created temp directory: $TEMP_DIR${NC}"

# Copy all webfront files to temp directory
echo -e "${YELLOW}Copying web files from $SRC_DIR to temp directory...${NC}"
cp -r "$SRC_DIR"/* "$TEMP_DIR"/

# Initialize git in temp directory
cd "$TEMP_DIR"
git init

# Set Git configuration - this fixes the "empty ident name" error
echo -e "${YELLOW}Setting Git configuration...${NC}"
# Use global config if available, otherwise use default values
GIT_USER_NAME=$(git config --global user.name || echo "GitHub Pages Deployment")
GIT_USER_EMAIL=$(git config --global user.email || echo "noreply@example.com")
git config user.name "$GIT_USER_NAME"
git config user.email "$GIT_USER_EMAIL"

# Create and checkout gh-pages branch
git checkout -b gh-pages

# Add all files
echo -e "${YELLOW}Adding all files to git...${NC}"
git add .

# Create .nojekyll file to bypass Jekyll processing
touch .nojekyll
git add .nojekyll

# Configure git to push to the original repository using token authentication
echo -e "${YELLOW}Configuring remote repository...${NC}"

# Ask for GitHub token if not provided
if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${YELLOW}GitHub token not found in environment.${NC}"
    read -sp "Enter your GitHub personal access token: " GITHUB_TOKEN
    echo ""
    if [ -z "$GITHUB_TOKEN" ]; then
        echo -e "${RED}No token provided. Will attempt to push with existing credentials.${NC}"
    fi
fi

# Extract GitHub username and repo from the URL - fixes the double .git issue
if [[ "$REPO_URL" =~ github\.com[:/]([^/]+)/([^/.]+)(\.git)? ]]; then
    GITHUB_USER="${BASH_REMATCH[1]}"
    GITHUB_REPO="${BASH_REMATCH[2]}"
    
    # If we have a token, use it in the remote URL
    if [ ! -z "$GITHUB_TOKEN" ]; then
        # Ensure we don't add .git if it's already in the repo URL
        TOKEN_URL="https://${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${GITHUB_REPO}.git"
        git remote add origin "$TOKEN_URL"
        echo -e "${GREEN}Remote configured with token authentication.${NC}"
        # Debug output to verify URL
        echo -e "${YELLOW}Using repository: github.com/${GITHUB_USER}/${GITHUB_REPO}${NC}"
    else
        git remote add origin "$REPO_URL"
        echo -e "${YELLOW}Remote configured with standard URL. Authentication may be required.${NC}"
    fi
else
    echo -e "${YELLOW}Could not parse GitHub repository details. Using original URL.${NC}"
    git remote add origin "$REPO_URL"
fi

# Commit changes
echo -e "${YELLOW}Committing changes...${NC}"
git commit -m "Deploy to GitHub Pages - $(date)" --quiet

# Push to GitHub with force
echo -e "${YELLOW}Pushing to GitHub...${NC}"
# Ensure we're on gh-pages branch before pushing
git branch
git push -f origin gh-pages || {
    echo -e "${RED}Push failed. You may need to provide credentials or use a personal access token.${NC}"
    echo -e "${YELLOW}Try: git push -f https://USERNAME:TOKEN@github.com/username/$REPO_NAME.git gh-pages${NC}"
    exit 1
}

# Cleanup
echo -e "${YELLOW}Cleaning up temporary directory...${NC}"
cd "$REPO_ROOT"
rm -rf "$TEMP_DIR"

# Correct GitHub Pages URL
GITHUB_USER=$(echo "$REPO_URL" | sed -n 's/.*[:/]\([^/]*\)\/[^/]*\.git$/\1/p')
if [ -z "$GITHUB_USER" ]; then
    GITHUB_USER="your-username"
fi

echo -e "${GREEN}Deployment complete!${NC}"
echo -e "${GREEN}Your site should be available at: https://$GITHUB_USER.github.io/$REPO_NAME/${NC}"
echo -e "${YELLOW}Note: It might take a few minutes for the changes to reflect.${NC}"
