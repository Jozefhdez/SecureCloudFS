# SecureCloudFS

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)

**Your files, encrypted and secure in the cloud**

SecureCloudFS encrypts your files with AES-256 *before* they leave your computer. Even we can't see your data.

> **⚠️ Important**: To upload files, you must download and run the desktop client. The web app is only for viewing and downloading existing files.

## How to Use SecureCloudFS

### Web App (View & Download Only)
**The web app CANNOT upload files. Use the desktop client below for uploads.**

Access your files from any browser:

** [Open SecureCloudFS Web App](https://secure-cloud-fs.vercel.app)**

- ✅ View all your encrypted files
- ✅ Download files to your device
- ✅ Works on any device with internet

### Desktop Client
**You need this to upload files or sync folders.**

Download one file and run:

```bash
# 1. Download the client (one file only)
curl -O https://raw.githubusercontent.com/Jozefhdez/SecureCloudFS/main/securecloud.py

# 2. Install dependencies (first time only)
pip install requests cryptography watchdog python-dotenv oci supabase

# 3. Create an account
https://secure-cloud-fs.vercel.app/

# 4. Upload and sync a folder
python3 securecloud.py sync --email your@email.com --password yourpass --folder /path/to/folder
```

**Why both?** Files are encrypted on your computer before upload, so we need local software for security.
## Why SecureCloudFS?

- **True Privacy**: Files are encrypted *before* upload with your password
- **Access Anywhere**: Web interface works on any device
- **Auto Sync**: Desktop client syncs folders automatically (optional)
- **Free to Use**: No credit card required
- **Zero Knowledge**: We cannot see your files, even if we wanted to

## How Secure Is It?

- **AES-256 encryption** (military grade)
- **Your password = your key** (we never see it)
- **Encrypted before upload** (not even our servers can read your files)
- **User isolation** (each user's data is completely separate)

## Perfect For

- **Personal backup** of important documents
- **Cross-device file access** (work, home, travel)
- **Sensitive documents** that need encryption
- **Automatic folder syncing** for photographers, developers, etc.

## FAQ

**Q: Can I use just the web app?**
A: Only for viewing and downloading files. You need the desktop client to upload files securely.

**Q: Why can't I upload through the web?**
A: Files must be encrypted on YOUR computer before upload for true security. 

**Q: Do I need to install anything?**
A: Just Python and one small script. No complex setup required.

**Q: Can you see my files?**
A: No. They're encrypted with your password before leaving your computer.

**Q: What if I forget my password?**
A: Your files become unrecoverable. We cannot reset passwords.

**Q: Is it really free?**
A: Yes, the service is free to use.

---

**Made by Jozef Hernandez** | [LinkedIn](https://www.linkedin.com/in/jozefhdez/)
