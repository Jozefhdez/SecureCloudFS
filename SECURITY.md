# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Security Features

- **Local Encryption**: All files are encrypted locally using AES-256 before uploading
- **Zero Knowledge**: Cloud provider cannot access your files in plaintext
- **Secure Authentication**: User authentication handled by Supabase
- **Isolated Storage**: Each user can only access their own encrypted files

## Configuration Security

- Never commit `.env` files with real credentials
- Use the provided `.env.example` files as templates
- Keep your OCI private keys secure and never share them
- Rotate your API keys regularly

## Reporting Security Vulnerabilities

If you discover a security vulnerability, please send an email to [your-email@example.com].

Please do NOT create a public GitHub issue for security vulnerabilities.

## Best Practices

1. Always use strong passwords for your accounts
2. Keep your Python environment updated
3. Regularly update dependencies
4. Monitor your OCI usage and costs
5. Use the latest version of SecureCloudFS
