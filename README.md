# SecureCloudFS

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)

End-to-end encrypted cloud file storage with AES-256 encryption. Files are encrypted on your device before upload.

> **Important**: The web app is for viewing and downloading only. The desktop client to upload files.

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

## Project status and keys

- This repository is a toy/example project for local experimentation and is not a
	production service. The included client and sample keys are placeholders.
- You must provide your own service keys and configuration to run uploads or
	sync features. Do not use any embedded keys in production.
- To run the client locally, set environment variables (or a local `.env`) with
	your keys and endpoints, then run the client as shown above.

## Security

- AES-256 encryption
- Client-side encryption before upload
- Zero-knowledge architecture
- Password-derived encryption keys
- User data isolation with Row-Level Security
---

Made by Jozef Hernandez | [LinkedIn](https://www.linkedin.com/in/jozefhdez/)
