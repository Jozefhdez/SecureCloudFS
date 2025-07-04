# SecureCloudFS

**Encrypted virtual filesystem with automatic synchronization**

SecureCloudFS is a system that encrypts files locally using AES-256 before uploading them to Oracle Cloud Infrastructure (OCI), ensuring complete privacy even from the cloud provider. It uses Supabase for authentication and metadata management.

## Features

- **AES-256 Encryption**: All files are encrypted locally before uploading to the cloud
- **Automatic Synchronization**: Real-time monitoring of file changes
- **User Isolation**: Each user can only access their own files
- **Oracle Cloud Storage**: Scalable and secure storage
- **Supabase Authentication**: Secure user and session management
- **Integrated CLI**: Command-line tools for advanced management

## Technologies

- **Backend**: Python 3.8+
- **Encryption**: cryptography (AES-256 + PBKDF2)
- **Cloud Storage**: Oracle Cloud Infrastructure (OCI)
- **Authentication**: Supabase Auth
- **Database**: Supabase (PostgreSQL)
- **Monitoring**: watchdog

## Requirements

- Python 3.8 or higher
- Oracle Cloud Infrastructure account
- Configured Supabase project
- Internet access

## Quick Installation

1. **Clone repository**:
   ```bash
   git clone <your-repo>
   cd SecureCloudFS
   ```

2. **Run setup script**:
   ```bash
   ./setup.sh
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Configure database**:
   - Execute `setup_database.sql` in Supabase SQL Editor

## Detailed Configuration

### 1. Supabase Configuration

1. Create project at [Supabase](https://supabase.com)
2. Get project URL and public API Key
3. Execute `setup_database.sql` script in SQL Editor
4. Configure user authentication

### 2. Oracle Cloud Infrastructure Configuration

1. Create account at [Oracle Cloud](https://cloud.oracle.com)
2. Create an Object Storage bucket
3. Generate API Key and get necessary OCIDs
4. Configure OCI environment variables

### 3. Environment variables (.env)

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_API_KEY=your_public_api_key

# Oracle Cloud Infrastructure
OCI_USER_OCID=ocid1.user.oc1..your_user_ocid
OCI_KEY_FILE=/path/to/your/private_key.pem
OCI_FINGERPRINT=your_fingerprint
OCI_TENANCY_OCID=ocid1.tenancy.oc1..your_tenancy_ocid
OCI_REGION=us-ashburn-1
OCI_NAMESPACE=your_namespace
OCI_BUCKET_NAME=your_bucket
```

## Usage

### Main Interface

```bash
# Activate virtual environment
source venv/bin/activate

# Run SecureCloudFS
python scfs_sync.py
```

### CLI (Command Line Interface)

```bash
# Verify credentials
python scfs_cli.py --email your@email.com --password your_password auth

# List files
python scfs_cli.py --email your@email.com --password your_password list

# Sync specific folder
python scfs_cli.py --email your@email.com --password your_password sync /path/folder

# Download file
python scfs_cli.py --email your@email.com --password your_password download file.txt ./download/
```

## Security

- **Local encryption**: Files are encrypted using AES-256 before leaving your machine
- **Key derivation**: PBKDF2 with 100,000 iterations
- **User isolation**: Row Level Security in Supabase
- **JWT tokens**: Secure authentication with automatic expiration
- **Unique prefixes**: File separation by user in OCI

## Project Structure

```
SecureCloudFS/
├── scfs_sync.py          # Main application
├── scfs_cli.py           # Command line interface
├── scfs_api.py           # API for web dashboard
├── requirements.txt      # Python dependencies
├── setup.sh             # Installation script
├── setup_database.sql   # Database configuration
├── .env.example         # Environment variables template
├── README.md            # Documentation
└── web/                 # React frontend (optional)
    ├── src/
    ├── package.json
    └── ...
```

## Workflow

1. **Authentication**: User authenticates with Supabase
2. **Monitoring**: System monitors local folder for changes
3. **Encryption**: New/modified files are encrypted with AES-256
4. **Upload**: Encrypted files are uploaded to OCI with unique prefix
5. **Metadata**: File information is saved in Supabase
6. **Cleanup**: Temporary encrypted files are deleted

## Troubleshooting

### OCI connection error
- Verify API Key configuration
- Validate OCIDs and region
- Check bucket permissions

### Supabase authentication error
- Verify URL and API Key
- Check that user exists
- Validate RLS configuration

### Files not syncing
- Check folder permissions
- Review logs in `securecloud.log`
- Validate network connectivity

## API Reference

### SecureCloudFS

```python
# Initialize
scfs = SecureCloudFS(email, password, sync_folder)

# Sync specific file
scfs.sync_file("path/file.txt")

# Start automatic monitoring
scfs.start_monitoring()

# List user files
files = scfs.list_user_files()

# Download file
scfs.download_file(oci_object_name, local_path)
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## License

This project is under the MIT License. See `LICENSE` file for more details.

## Author

**Jozef Hernandez**
- GitHub: [@jozefhdez](https://github.com/jozefhdez)

## Acknowledgments

- [Supabase](https://supabase.com) for the backend platform
- [Oracle Cloud](https://cloud.oracle.com) for storage
- [cryptography](https://cryptography.io) for encryption tools
- [watchdog](https://github.com/gorakhargosh/watchdog) for file monitoring