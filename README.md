# SecureCloudFS

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)

**🔒 Your files, encrypted and secure in the cloud**

SecureCloudFS encrypts your files with AES-256 *before* they leave your computer. Even we can't see your data.

## 🚀 Start Using SecureCloudFS

### 🌐 Web App (Instant Access)
No installation needed. Use from any browser:

**👉 [Open SecureCloudFS Web App](https://secure-cloud-iof1dxs3d-jozefhdezs-projects.vercel.app/)**

1. Create your free account
2. Upload files (they get encrypted automatically)
3. Access from anywhere

### 💻 Desktop Sync (Optional)
Want automatic folder syncing? Install our desktop client:

```bash
# 1. Download and install
git clone https://github.com/Jozefhdez/SecureCloudFS.git
cd SecureCloudFS

# 2. Run the installer
./install.sh

# 3. Sync a folder automatically  
python3 scfs_sync.py --email your@email.com --password yourpassword --watch /path/to/folder
```

**That's it!** Any file you put in that folder gets encrypted and uploaded automatically.
## ❓ Why SecureCloudFS?

- **🔐 True Privacy**: Files are encrypted *before* upload with your password
- **🌐 Access Anywhere**: Web interface works on any device
- **🔄 Auto Sync**: Desktop client syncs folders automatically (optional)
- **🆓 Free to Use**: No credit card required
- **🛡️ Zero Knowledge**: We cannot see your files, even if we wanted to

## 🔧 Command Line Tools

### List your files
```bash
python3 scfs_cli.py --email your@email.com --password yourpass list
```

### Download a specific file
```bash
python3 scfs_cli.py --email your@email.com --password yourpass download --file "document.pdf" --output "./document.pdf"
```

### Sync a folder once
```bash
python3 scfs_cli.py --email your@email.com --password yourpass sync /path/to/folder
```

## 🔒 How Secure Is It?

- **AES-256 encryption** (military grade)
- **Your password = your key** (we never see it)
- **Encrypted before upload** (not even our servers can read your files)
- **User isolation** (each user's data is completely separate)

## 💡 Perfect For

- **Personal backup** of important documents
- **Cross-device file access** (work, home, travel)
- **Sensitive documents** that need encryption
- **Automatic folder syncing** for photographers, developers, etc.

## ⚡ Quick FAQ

**Q: Do I need to install anything?**
A: No! Use the web app instantly. Desktop sync is optional.

**Q: Can you see my files?**
A: No. They're encrypted with your password before leaving your computer.

**Q: What if I forget my password?**
A: Your files become unrecoverable. We cannot reset passwords.

**Q: Is it really free?**
A: Yes, the service is free to use.

## 🆘 Need Help?

1. Try the [Web App](https://secure-cloud-iof1dxs3d-jozefhdezs-projects.vercel.app/) first
2. Check your email/password if login fails
3. Open an issue on GitHub for technical problems

---

**Made by Jozef Hernandez** | [LinkedIn](https://www.linkedin.com/in/jozefhdez/)