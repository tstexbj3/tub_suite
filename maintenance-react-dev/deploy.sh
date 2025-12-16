#!/bin/bash
# One-command build and deploy script

set -e  # Exit on error

echo "🏗️  Building React app..."
npm run build

echo ""
echo "🔄 Updating template hash..."
bash update-hash.sh

echo ""
echo "✅ Deploy complete!"
echo ""
echo "🚀 Restart bench and refresh browser to see changes"
