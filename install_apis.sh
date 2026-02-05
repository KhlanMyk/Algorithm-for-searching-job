#!/bin/bash
# API Installation Script
# Installs optional API client libraries for better job searching

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║  Job Monitoring System - API Setup                                ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if venv is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not activated!"
    echo "Run: source venv/bin/activate"
    exit 1
fi

echo "📦 Installing optional API client libraries..."
echo ""

# Try to install API libraries
echo "1️⃣  Installing Indeed API client..."
pip install indeed-api 2>/dev/null || echo "   ℹ️  indeed-api not available on PyPI (will use REST API)"

echo ""
echo "2️⃣  Installing LinkedIn Jobs Crawler..."
pip install linkedin-jobs-crawler 2>/dev/null || echo "   ℹ️  linkedin-jobs-crawler optional (web scraping fallback available)"

echo ""
echo "3️⃣  Installing optional Selenium for LinkedIn..."
pip install selenium 2>/dev/null || echo "   ℹ️  selenium optional (for enhanced LinkedIn scraping)"

echo ""
echo "✅ Installation complete!"
echo ""
echo "📌 Next Steps:"
echo "   1. Get your API keys from:"
echo "      - Indeed: https://opensource.indeedeng.io/api-documentation/"
echo "      - LinkedIn: https://www.linkedin.com/developers/apps"
echo ""
echo "   2. Add keys to .env file:"
echo "      INDEED_PUBLISHER_ID=your_id"
echo "      LINKEDIN_API_KEY=your_key"
echo ""
echo "   3. Run the system:"
echo "      python main.py"
echo ""
