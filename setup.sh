#!/bin/bash

# Setup script for Craft Auto-Sort
# This script sets up the virtual environment and dependencies

set -e  # Exit on error

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "========================================"
echo "Craft Auto-Sort Setup"
echo "========================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3 first: brew install python3"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment and install dependencies
echo "📦 Installing dependencies..."
source venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet requests python-dotenv
echo "✓ Dependencies installed"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found"
    echo "Creating .env from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✓ .env file created"
        echo ""
        echo "⚠️  IMPORTANT: Please edit .env and add your Craft API key!"
        echo "   Run: nano .env"
    else
        echo "❌ Error: .env.example not found"
        exit 1
    fi
else
    echo "✓ .env file exists"
fi
echo ""

# Make scripts executable
chmod +x craft_unsorted_sorter.py
chmod +x setup_cron.sh
echo "✓ Scripts made executable"
echo ""

echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Craft API key:"
echo "   nano .env"
echo ""
echo "2. Test the script:"
echo "   ./craft_unsorted_sorter.py"
echo ""
echo "3. Install the cron job (runs every Friday at 9 AM):"
echo "   ./setup_cron.sh"
echo ""
echo "View logs:"
echo "   tail -f ~/Library/Logs/CraftAutoSort/craft_sort_*.log"
echo ""
