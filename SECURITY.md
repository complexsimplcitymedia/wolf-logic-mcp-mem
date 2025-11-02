# Security Policy

## Protecting Sensitive Data

This MCP memory server handles potentially sensitive data. Follow these security best practices to guard your data with your life:

### 1. Environment Variables

- **Never commit `.env` files** to version control
- Always use `.env.example` as a template and create your own `.env` file locally
- Generate strong, unique values for all secrets (API_KEY, ENCRYPTION_KEY, SESSION_SECRET)
- Use a minimum of 32 characters for encryption keys

### 2. Data Encryption

- All sensitive data stored in memory should be encrypted at rest
- Use the `ENCRYPTION_KEY` environment variable for encrypting/decrypting sensitive data
- Rotate encryption keys periodically following your security policy

### 3. Authentication & Authorization

- Require API key authentication for all server endpoints
- Implement rate limiting to prevent abuse
- Use HTTPS in production environments
- Validate and sanitize all input data

### 4. Access Control

- Configure `ALLOWED_ORIGINS` carefully to restrict CORS access
- Limit access to the memory storage path using file system permissions
- Run the server with minimal required privileges

### 5. Data Storage

- Store memory data in a secure location with appropriate file permissions
- Regularly backup encrypted data
- Implement data retention policies and securely delete old data
- Never store plaintext credentials or secrets in memory

### 6. Local Development

- Use separate credentials for development and production
- Don't share your `.env` file or credentials with others
- Keep your local environment updated with security patches

### 7. Monitoring & Logging

- Enable logging for security events (failed authentication, unusual access patterns)
- Regularly review logs for suspicious activity
- Ensure logs don't contain sensitive data
- Implement log rotation to prevent disk space issues

## Reporting Security Vulnerabilities

If you discover a security vulnerability in this project, please report it responsibly:

1. **Do not** open a public issue
2. Email the maintainer directly with details
3. Allow time for the vulnerability to be patched before public disclosure

## Security Updates

- Keep all dependencies up to date
- Monitor security advisories for dependencies
- Apply security patches promptly

## Compliance

When deploying this MCP memory server:

- Ensure compliance with relevant data protection regulations (GDPR, CCPA, etc.)
- Implement appropriate data handling procedures
- Document your security measures
- Conduct regular security audits

---

**Remember: Guard your data with your life. Security is not optional.**
