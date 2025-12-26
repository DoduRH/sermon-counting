#!/bin/bash

# Sermon Counting Dashboard - Deployment Script
# Makes it easy to deploy your visualizations to GitHub Pages

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Sermon Counting Dashboard Deployment${NC}"
echo "=========================================="

# Check if output directory exists
if [ ! -d "output" ]; then
    echo -e "${YELLOW}⚠️  Error: 'output' directory not found${NC}"
    exit 1
fi

cp html/index.html output/index.html

# Check if gh-pages is installed
if ! npm list --depth=0 | grep -q gh-pages; then
    echo -e "${BLUE}📦 Installing gh-pages...${NC}"
    npm install --save-dev gh-pages
fi

echo -e "${BLUE}📊 Deploying to GitHub Pages...${NC}"

# Run gh-pages
npx gh-pages -d output

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "Your dashboard is now live at:"
echo "https://github.com/dodurh/sermon-counting/settings/pages"
echo ""
echo "Or visit the live site at:"
echo "https://dodurh.github.io/sermon-counting"
echo ""
echo "💡 Tip: Update your graphs and run this script again to refresh!"
