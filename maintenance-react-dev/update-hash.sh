#!/bin/bash
# Auto-update maintenance.html with latest build hashes

echo "🔍 Finding latest asset hashes..."

# Get the JS and CSS filenames
JS_FILE=$(ls ../tub_suite/public/maintenance/assets/index-*.js 2>/dev/null | head -1 | xargs basename)
CSS_FILE=$(ls ../tub_suite/public/maintenance/assets/index-*.css 2>/dev/null | head -1 | xargs basename)

if [ -z "$JS_FILE" ] || [ -z "$CSS_FILE" ]; then
    echo "❌ Error: Build files not found. Run 'npm run build' first."
    exit 1
fi

echo "   JS:  $JS_FILE"
echo "   CSS: $CSS_FILE"

# Update maintenance.html
TEMPLATE="../tub_suite/www/maintenance.html"

echo "📝 Updating $TEMPLATE..."

# Use sed to update both lines
sed -i "s|/assets/tub_suite/maintenance/assets/index-[^\.]*\.js|/assets/tub_suite/maintenance/assets/$JS_FILE|g" "$TEMPLATE"
sed -i "s|/assets/tub_suite/maintenance/assets/index-[^\.]*\.css|/assets/tub_suite/maintenance/assets/$CSS_FILE|g" "$TEMPLATE"

echo "✅ Template updated successfully!"
echo ""
echo "🚀 Next steps:"
echo "   1. Restart bench: bench restart (or Ctrl+C and 'bench start')"
echo "   2. Refresh browser with Ctrl+Shift+R"
