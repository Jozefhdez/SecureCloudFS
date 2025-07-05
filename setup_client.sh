#!/bin/bash
# SecureCloudFS Client Setup Script
# Quick installation for end users

echo "🔐 SecureCloudFS Client Setup"
echo "=============================="
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION detected"

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip is required but not installed."
    echo "Please install pip3"
    exit 1
fi

echo "✅ pip detected"

# Install dependencies
echo ""
echo "📦 Installing SecureCloudFS dependencies..."
pip3 install -r requirements-client.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "🎉 SecureCloudFS Client Setup Complete!"
echo ""
echo "Usage Examples:"
echo "==============="
echo ""
echo "1. List your files:"
echo "   python3 securecloud_client.py --email your@email.com --password yourpass list"
echo ""
echo "2. Download a file:"
echo "   python3 securecloud_client.py --email your@email.com --password yourpass download --file 'document.pdf' --output './document.pdf'"
echo ""
echo "3. Start automatic folder sync:"
echo "   python3 securecloud_sync.py --email your@email.com --password yourpass --watch /path/to/folder"
echo ""
echo "🌐 Web Dashboard: https://your-app.vercel.app"
echo "📚 Documentation: https://github.com/Jozefhdez/SecureCloudFS"
echo ""
echo "Your files are encrypted locally before being sent to the cloud."
echo "Even we cannot access your data without your password! 🔒"
