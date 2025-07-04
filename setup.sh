#!/bin/bash

echo "=== SecureCloudFS Setup Script ==="
echo "This script will configure SecureCloudFS on your system"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    exit 1
fi

echo "[OK] Python 3 found: $(python3 --version)"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Update pip
echo "Updating pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "[OK] SecureCloudFS installed successfully!"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and configure your credentials"
echo "2. Execute setup_database.sql script in Supabase"
echo "3. Configure Oracle Cloud Infrastructure (OCI)"
echo "4. Run: source venv/bin/activate && python scfs_sync.py"
echo ""
echo "For more information, see README.md"
