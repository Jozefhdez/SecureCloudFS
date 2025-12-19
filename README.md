# SecureCloudFS

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)

End-to-end encrypted cloud file storage with AES-256 encryption. Files are encrypted on your device before upload.

> **Important**: The web app is for viewing and downloading only. Use the desktop client to upload files.

## Quick Start

### Web App
Access at [secure-cloud-fs.vercel.app](https://secure-cloud-fs.vercel.app)
- View encrypted files
- Download files
- Works on any device

### Desktop Client
Required for uploading and syncing files.

```bash
# Download client
curl -O https://raw.githubusercontent.com/Jozefhdez/SecureCloudFS/main/securecloud.py

# Install dependencies
pip install requests cryptography watchdog python-dotenv oci supabase

# Create account at https://secure-cloud-fs.vercel.app/

# Upload and sync folder
python3 securecloud.py sync --email your@email.com --password yourpass --folder /path/to/folder
```

## Security

- AES-256 encryption
- Client-side encryption before upload
- Zero-knowledge architecture
- Password-derived encryption keys
- User data isolation with Row-Level Security

## Features

- End-to-end encryption
- Cross-device access
- Automatic folder syncing
- Web-based file management
- No credit card required

## FAQ

**Q: Why can't I upload through the web?**
A: Client-side encryption requires local software to ensure files are encrypted before leaving your device.

**Q: Can you access my files?**
A: No. Files are encrypted with your password before upload. We cannot decrypt them.

**Q: What if I forget my password?**
A: Files become permanently unrecoverable. Password reset is not possible.

---

Made by Jozef Hernandez | [LinkedIn](https://www.linkedin.com/in/jozefhdez/)
