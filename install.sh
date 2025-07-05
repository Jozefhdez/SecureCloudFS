#!/bin/bash

echo "🔒 SecureCloudFS Client Setup"
echo "============================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "   Please install Python 3.8+ and try again."
    exit 1
fi

echo "✅ Python 3 found"

# Check if pip is installed
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "❌ pip is required but not installed."
    echo "   Please install pip and try again."
    exit 1
fi

echo "✅ pip found"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
if command -v pip3 &> /dev/null; then
    pip3 install -r requirements.txt
else
    pip install -r requirements.txt
fi

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Copy client configuration
echo ""
echo "⚙️  Setting up configuration..."
cp .env.client .env
echo "✅ Client configured to use hosted SecureCloudFS service"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📖 Usage:"
echo "  # List your files:"
echo "  python3 scfs_cli.py --email your@email.com --password yourpass list"
echo ""
echo "  # Start auto-sync for a folder:"
echo "  python3 scfs_sync.py --email your@email.com --password yourpass --watch /path/to/folder"
echo ""
echo "  # Or use the web app: https://secure-cloud-iof1dxs3d-jozefhdezs-projects.vercel.app/"
echo ""
echo "⚠️  Create your account at: https://secure-cloud-iof1dxs3d-jozefhdezs-projects.vercel.app/"
