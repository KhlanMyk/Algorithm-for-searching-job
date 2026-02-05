#!/bin/bash

# Quick Start Script for Job Monitoring System
# This script sets up and runs the job monitoring system

set -e

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                                                                    ║"
echo "║     🚀 Job & Internship Monitoring System - Quick Start 🚀       ║"
echo "║                                                                    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅ Python $PYTHON_VERSION found"

# Check if in correct directory
if [ ! -f "main.py" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Step 1: Create virtual environment if needed
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Step 2: Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Step 3: Install dependencies
echo ""
echo "📚 Installing dependencies from requirements.txt..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "✅ Dependencies installed"

# Step 4: Run setup if .env doesn't exist
echo ""
if [ ! -f ".env" ]; then
    echo "⚙️  Configuration wizard needed..."
    echo ""
    python3 setup.py
else
    echo "✅ .env file exists, skipping configuration"
    echo ""
    read -p "Do you want to reconfigure credentials? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm .env
        python3 setup.py
    fi
fi

# Step 5: Display final message
echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ Setup Complete!                             ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📖 Next steps:"
echo "   1. Review your .env file with your credentials"
echo "   2. Customize keywords in config/config.py if desired"
echo "   3. Run: python3 main.py"
echo ""
echo "To start the monitoring system now, type:"
echo "   python3 main.py"
echo ""
