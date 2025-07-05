# SecureCloudFS User Guide

## What is SecureCloudFS?

SecureCloudFS is a secure file storage service that encrypts your files locally before uploading them to the cloud. This means:

- ✅ **Your files are private**: Even we cannot see your data
- ✅ **Military-grade encryption**: AES-256 encryption
- ✅ **Easy to use**: Web interface + optional sync client
- ✅ **Cross-platform**: Works on any device

## Getting Started

### Option 1: Web Only (Easiest)
1. Visit [SecureCloudFS Web Dashboard](https://your-app.vercel.app)
2. Create your account
3. Upload, download, and manage files through your browser
4. Done! No installation required.

### Option 2: Automatic Sync (Advanced)
For automatically syncing local folders:

1. **Download the client**: Download from [GitHub Releases](https://github.com/Jozefhdez/SecureCloudFS/releases)
2. **Install**: Run `./setup_client.sh` (Mac/Linux) or follow manual installation
3. **Sync**: Use `python3 securecloud_sync.py` to sync folders automatically

## Client Installation

### Requirements
- Python 3.8 or higher
- Internet connection

### Quick Setup
```bash
# Download and extract
curl -L https://github.com/Jozefhdez/SecureCloudFS/archive/main.zip -o securecloud.zip
unzip securecloud.zip
cd SecureCloudFS-main

# Install dependencies
pip3 install -r requirements-client.txt

# You're ready to use the client!
```

## Client Usage

### List Files
```bash
python3 securecloud_client.py --email your@email.com --password yourpass list
```

### Download File
```bash
python3 securecloud_client.py --email your@email.com --password yourpass download --file "document.pdf" --output "./document.pdf"
```

### Auto-Sync Folder
```bash
python3 securecloud_sync.py --email your@email.com --password yourpass --watch /path/to/your/folder
```

## Security

- **Local Encryption**: Files are encrypted on your device before upload
- **Zero Knowledge**: We cannot decrypt your files without your password
- **Secure Transport**: All communications use HTTPS
- **User Isolation**: Each user can only access their own files
- **Open Source**: Code is publicly auditable

## Support

- 🌐 Web Dashboard: [https://your-app.vercel.app](https://your-app.vercel.app)
- 📚 Documentation: [GitHub Repository](https://github.com/Jozefhdez/SecureCloudFS)
- 🐛 Issues: [GitHub Issues](https://github.com/Jozefhdez/SecureCloudFS/issues)

## FAQ

**Q: Can you see my files?**
A: No. Files are encrypted with your password before leaving your device.

**Q: What happens if I forget my password?**
A: Your files cannot be recovered. Make sure to remember your password.

**Q: Is there a file size limit?**
A: Currently 100MB per file. Contact us for larger files.

**Q: How much does it cost?**
A: The service is currently free during beta. Pricing TBA.

---

Made with ❤️ by [Jozef Hernandez](https://github.com/Jozefhdez)
