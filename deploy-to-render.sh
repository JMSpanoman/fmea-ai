#!/bin/bash

# 🚀 Deploy Foton aiQMS to Render
# This script helps you deploy your FMEA system to Render

echo "🚀 Deploying Foton aiQMS to Render..."
echo "=================================="

# Check if we're in the right directory
if [ ! -f "render.yaml" ]; then
    echo "❌ Error: render.yaml not found. Please run this script from the project root."
    exit 1
fi

# Check if git is clean
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Warning: You have uncommitted changes."
    echo "   Please commit your changes before deploying:"
    echo "   git add . && git commit -m 'Your commit message'"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment cancelled."
        exit 1
    fi
fi

# Push to GitHub
echo "📤 Pushing to GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo "✅ Successfully pushed to GitHub!"
else
    echo "❌ Failed to push to GitHub. Please check your git configuration."
    exit 1
fi

echo ""
echo "🎯 Next Steps:"
echo "=============="
echo "1. Go to https://dashboard.render.com"
echo "2. Click 'New +' → 'Blueprint'"
echo "3. Connect your GitHub repository: JMSpanoman/fmea-ai"
echo "4. Render will automatically deploy both services from render.yaml"
echo ""
echo "📋 Services to be deployed:"
echo "  • Backend: fmea-backend (https://fmea-backend.onrender.com)"
echo "  • Frontend: fmea-frontend (https://fmea-frontend.onrender.com)"
echo ""
echo "🔧 Environment Variables to set in Render Dashboard:"
echo "  Backend:"
echo "    - OPENAI_API_KEY: Your OpenAI API key"
echo "  Frontend:"
echo "    - All variables are already configured in render.yaml"
echo ""
echo "📖 For detailed instructions, see: RENDER_DEPLOYMENT_GUIDE.md"
echo ""
echo "✅ Deployment preparation complete!"

